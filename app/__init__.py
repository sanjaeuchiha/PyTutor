from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

app = Flask(__name__)
SQLALCHEMY_DATABASE_URI='mysql://sanjaeuchiha@localhost/c9'
app.config.from_object('config')
db = SQLAlchemy(app)


lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

from app import views, models

