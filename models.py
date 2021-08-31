import os
from sqla_wrapper import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///db.sqlite"))  # this connects to a database either on Heroku or on localhost


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    photo = db.Column(db.String(100),default='-206800941_281114517')
    have_profile_picture = db.Column(db.Integer,default=0)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    reg_date = db.Column(db.DateTime, default=datetime.utcnow())
    desc = db.Column(db.Text,default='Description')
    is_banned = db.Column(db.Integer,default=0)
    api_key = db.Column(db.String(128),default="")

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    frm = db.Column(db.Integer)
    to = db.Column(db.Integer)
    text = db.Column(db.Text)
    attachments = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow())
    is_read = db.Column(db.Integer, default=0)
    is_sticker = db.Column(db.Integer, default=0)
class Chats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    frm = db.Column(db.Integer)
    to = db.Column(db.Integer)
