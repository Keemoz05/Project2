from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import pytz
from datetime import datetime
from sqlalchemy import event

def remove_microseconds(r):
    if r is not None:
        return r.replace(microsecond=0)
    return r

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    contactinfo = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(150))
    lost_item = db.relationship('Lostitem')
    found_item = db.relationship('Founditem')


class Lostitem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))             
    description = db.Column(db.String(999999))
    date_lost = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.timezone('Asia/Kuala_Lumpur')).replace(microsecond=0))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_file = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(1000), nullable=False)


class Founditem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(999999))
    date_found = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.timezone('Asia/Kuala_Lumpur')).replace(microsecond=0))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_file = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(1000), nullable=False)

@event.listens_for(Lostitem, 'before_insert')
@event.listens_for(Lostitem, 'before_update')
def before_saving_lostitem(mapper, connection, target):
    target.date_lost = remove_microseconds(target.date_lost)

@event.listens_for(Founditem, 'before_insert')
@event.listens_for(Founditem, 'before_update')
def before_saving_founditem(mapper, connection, target):
    target.date_found = remove_microseconds(target.date_found)