from app import db
from flask import Flask, url_for

# Task Model Definition
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.String(36), primary_key=True)
    operation = db.Column(db.String(30), index=True)
    state = db.Column(db.String(30), index=True)
    complete = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref='tasks', lazy='dynamic')
    result = db.relationship('Result', backref='results', lazy='dynamic')

    # Getting the string representation of model on querying
    def __repr__(self):
        return '<Task {}>'.format(self.id)

    # Getting the url for the Task operation
    def get_url(self):
        return url_for('get_task_info', task_id=self.id, _external=True)

    # Getting information of the Task model entries in JSON representation
    def export_data(self):
        return {
            'task_id': self.id,
            'self_url': self.get_url(),
            'operation': self.operation,
            'state': self.state,
            'complete': self.complete,
            'export_url': url_for('get_export_info', task_id=self.id, _external=True),
            'import_url': url_for('get_import_info', task_id=self.id, _external=True)
        }


# User Model Definition
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), index=True)
    name = db.Column(db.String(64), index=True)
    age = db.Column(db.Integer)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), index=True)
    address = db.Column(db.String(300))
    record_date = db.Column(db.Date)

    # Getting the string representation of model on querying
    def __repr__(self):
        return '<User {}>'.format(self.id)

    # Getting the url for the import operation on User model
    def get_url(self):
        return url_for('get_import_info', task_id=self.task_id, _external=True)


# Result Model Definition
class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), index=True)
    name = db.Column(db.String(300))
    path = db.Column(db.String(300))
    data = db.Column(db.LargeBinary)

    # Getting the string representation of model on querying
    def __repr__(self):
        return '<Result {}>'.format(self.id)

    # Getting the url for the export entries saved on Result model
    def get_url(self):
        return url_for('get_export_info', task_id=self.task_id, _external=True)


# RevokedTask Model Definition
class RevokedTask(db.Model):
    __tablename__ = 'Revoked Tasks'
    task_id = db.Column(db.String(36), primary_key=True)

    # Getting the string representation of model on querying
    def __repr__(self):
        return '<Revoked Tasks {}>'.format(self.task_id)
