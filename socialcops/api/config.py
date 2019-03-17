import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Keeping track of various configurations of the Flask app
class Config(object):
    ALLOWED_EXTENSIONS = set(['csv'])
    UPLOAD_FOLDER = './files/uploads/'
    DOWNLOAD_FOLDER = './files/downloads/'
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        'uUHQMFSPB9H7G4bGwzFLDetrIyb4M8tj'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or \
        'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or \
        'redis://localhost:6379/0'
