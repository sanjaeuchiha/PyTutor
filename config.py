import os

basedir = os.path.abspath(os.path.dirname(__file__))

#SERVER_BASE="http://localhost"
SERVER_BASE="http://localhost:5000"
UPLOAD_FOLDER = basedir+'/app/static/uploads'
ALLOWED_EXTENSIONS = set(['csv'])
MAX_CONTENT_LENGTH = 1 * 1024 * 1024

CRSF_ENABLED = True
SECRET_KEY= 'fsfsfafasfN?*sfsdf'

SQLALCHEMY_DATABASE_URI='mysql://root:''@localhost/c9'
#SQLALCHEMY_DATABASE_URI='mysql://root:''@localhost/timetable'
