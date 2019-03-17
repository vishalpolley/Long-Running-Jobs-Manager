import os
import csv
from celery import Celery
from celery.result import AsyncResult
from celery.exceptions import Ignore
from celery.task.control import revoke
from celery.app.task import Task as celery_task
from io import StringIO
from io import TextIOWrapper
from datetime import datetime
from werkzeug.utils import secure_filename
from billiard.exceptions import Terminated
from app import app, db, make_celery
from app.models import User, Task, Result, RevokedTask
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, make_response, \
                request, jsonify, redirect, url_for

celery = make_celery(app)

# Error Handlers
class ValidationError(ValueError):
    pass

@app.errorhandler(ValidationError)
def bad_request(e):
    response = jsonify({'status': 400, 'error': 'bad request',
                        'message': e.args[0]})
    response.status_code = 400
    return response

@app.errorhandler(404)
def not_found(e):
    response = jsonify({'status': 404, 'error': 'not found',
                        'message': 'invalid resource URI'})
    response.status_code = 404
    return response

@app.errorhandler(405)
def method_not_supported(e):
    response = jsonify({'status': 405, 'error': 'method not supported',
                        'message': 'the method is not supported'})
    response.status_code = 405
    return response

@app.errorhandler(500)
def internal_server_error(e):
    response = jsonify({'status': 500, 'error': 'internal server error',
                        'message': e.args[0]})
    response.status_code = 500
    return response


# Allowed File Function
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# CSV upload Celery Task
@celery.task(name='tasks.upload', bind=True, throws=(Terminated,))
def csv_upload(self, path):
    file_path = path
    # Creating a new Task and assigning state to PROCESSING
    task_id = self.request.id
    task = Task(id=task_id, operation='Upload', state='PROCESSING')
    db.session.add(task)
    db.session.commit()
    with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        fields = next(csvreader)
        # Deleting all previous entries
        # db.session.query(User).delete()
        # db.session.commit()
        for row in csvreader:
            # Keeping track of AsyncResult state
            if(AsyncResult(task_id, app=celery).state == 'PENDING'):
                date = datetime.strptime(row[5], "%Y-%m-%d").date()
                # Adding user to User model
                user = User(name=row[0], age=row[1], phone=row[2],
                            email=row[3], address=row[4], record_date=date, task_id=task_id)
                db.session.add(user)
                db.session.commit()
            else:
                # Revoke Action on Upload Operation
                if(AsyncResult(task_id, app=celery).state == 'REVOKED'):
                    # Deleting all user entries on Revoke Action
                    entries = User.query.filter_by(task_id=task_id)
                    for entry in entries:
                        db.session.delete(entry)
                    # Keeping track of Revoked Tasks
                    rev = RevokedTask(task_id=task_id)
                    db.session.add(rev)
                    db.session.commit()
                    # Updating status of Task to REVOKED
                    task = Task.query.filter_by(id=task_id).first()
                    task.state = 'REVOKED'
                    db.session.add(task)
                    db.session.commit()
                    # Performing Revoke Operation
                    revoke(task_id, terminate=True, signal='SIGKILL')
                    raise Ignore
                # Pause Action on Upload Operation
                task = Task.query.filter_by(id=task_id).first()
                task.state = 'PAUSED'
                db.session.commit()
                return 'Uploading Operation Paused!!'
        # Success Action on Upload Operation
        task = Task.query.filter_by(id=task_id).first()
        task.state = 'SUCCESS'
        task.complete = True
        db.session.commit()
        return 'Uploaded Data!!'


# CSV result db commit function
def csv_result(csvList, task_id):
    # Generating the csv filename and file_path
    filename = task_id+'.csv'
    file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
    csvwriter = csv.writer(open(file_path, "w"))
    for row in csvList:
        # Keeping track of AsyncResult state
        if(AsyncResult(task_id, app=celery).state == 'PENDING'):
            csvwriter.writerow(row)
        else:
            # Revoke Action on Download Operation
            if(AsyncResult(task_id, app=celery).state == 'REVOKED'):
                # Keeping track of Revoked Tasks
                rev = RevokedTask(task_id=task_id)
                db.session.add(rev)
                db.session.commit()
                # Updating status of Task to REVOKED
                task = Task.query.filter_by(id=task_id).first()
                task.state = 'REVOKED'
                db.session.add(task)
                db.session.commit()
                # Performing Revoke Operation
                revoke(task_id, terminate=True, signal='SIGKILL')
                raise Ignore
            # Pause Action on Download Operation
            task = Task.query.filter_by(id=task_id).first()
            task.state = 'PAUSED'
            db.session.commit()
            return False
    # Writing csv data to Result model
    _file = open(file_path, 'rb')
    result = Result(task_id=task_id, name=filename, path=file_path, data=_file.read())
    db.session.add(result)
    db.session.commit()
    # Success Action on Download Operation
    task = Task.query.filter_by(id=task_id).first()
    task.state = 'SUCCESS'
    task.complete = True
    db.session.commit()
    return True


# CSV download Celery Task
@celery.task(name='tasks.download', bind=True, throws=(Terminated,))
def csv_download(self, _from, _till):
    csvList = []
    # Creating a new Task and assigning state to PROCESSING
    task_id = self.request.id
    task = Task(id=task_id, operation='Download', state='PROCESSING')
    db.session.add(task)
    db.session.commit()
    # Filtering out the User entries
    from_date = _from
    till_date = _till
    users = User.query.filter(User.record_date.between(from_date, till_date))
    for user in users:
        # Keeping track of AsyncResult state
        if(AsyncResult(task_id, app=celery).state == 'PENDING'):
            csvList.append([user.name,user.age,user.phone,user.email,
                            user.address,user.record_date.strftime("%Y-%m-%d")])
        else:
            break
    # Sending csvList to csv_result Function
    res = csv_result(csvList, task_id)
    if(res == False):
        # Pause Action on Download Operation
        task = Task.query.filter_by(id=task_id).first()
        task.state = 'PAUSED'
        db.session.commit()
        return "Downloading Operation Paused!!"
    return 'Downloaded Data!!'


# Index Page Task Route
@app.route('/')
def upload_file():
    return render_template('main.html')

# Download Operation Task Route
@app.route('/tasks/download', methods=['GET'])
def downloader():
    if request.method == 'GET':
        _from = request.args.get('from')
        _till = request.args.get('till')
        # Sending task to celery worker
        csv_download.delay(_from, _till)
        return jsonify({}), 200

# Upload Operation Task Route
@app.route('/tasks/upload', methods=['POST'])
def uploader():
    if request.method == 'POST':
        _file = request.files['file']
        if _file and allowed_file(_file.filename):
            filename = secure_filename(_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            _file.save(file_path)
            # Sending task to celery worker
            csv_upload.delay(file_path)
            return jsonify({}), 201


# Tasks Info Routes
@app.route('/tasks/', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': [task.get_url() for task in
                                Task.query.all()]})

@app.route('/tasks/<string:task_id>', methods=['GET'])
def get_task_info(task_id):
    return jsonify(Task.query.get_or_404(task_id).export_data())

# Import and Export Operation Routes
@app.route('/exports/<string:task_id>', methods=['GET'])
def get_export_info(task_id):
    return jsonify(Result.query.get_or_404(task_id).export_data())

@app.route('/imports/<string:task_id>', methods=['GET'])
def get_import_info(task_id):
    return jsonify(User.query.get_or_404(task_id).export_data())


# Pause, Resume and Stop Task Routes
@app.route('/tasks/<string:task_id>/pause', methods=['GET'])
def pause_operation(task_id):
    celery_task.update_state(self=celery, task_id=task_id, state='PAUSING')
    return jsonify({'task_id': task_id, 'status': AsyncResult(task_id, app=celery).state, 'message': 'Task Paused!!'}), 200

@app.route('/tasks/<string:task_id>/stop', methods=['GET'])
def revoke_operation(task_id):
    celery_task.update_state(self=celery, task_id=task_id, state='REVOKED')
    return jsonify({'task_id': task_id, 'status': AsyncResult(task_id, app=celery).state, 'message': 'Task Stopped!!'}), 200

# @app.route('/tasks/<string:task_id>/resume', methods=['GET'])
# def resume_operation(task_id):
#     celery_task.update_state(self=celery, task_id=task_id, state='PROCESSING')
#     return jsonify({'task_id': task_id, 'status': AsyncResult(task_id, app=celery).state, 'message': 'Task Resumed!!'}), 200
