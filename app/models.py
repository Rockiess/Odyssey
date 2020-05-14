# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 14:41:13 2020
models
@author: redba
"""

from flask import url_for
from datetime import datetime
from app import db #database
from werkzeug.security import generate_password_hash, check_password_hash #Password hashing
from flask_login import UserMixin #Handle log-in statuses
from app import login #Used to load the user when going through pages
import base64
from datetime import datetime, timedelta
import os

#requesting a collection of users
class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },

        }
        return data

class User(PaginatedAPIMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    devices = db.relationship('Device', backref='owner', lazy='dynamic')
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            '_links': {
                'self': url_for('api.get_user', id=self.id),
            }
        }
        if include_email:
            data['email'] = self.email
        return data
    
    def from_dict(self, data, new_user=False):
        for field in ['username', 'email']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b16encode(os.urandom(4)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user
            

#device
class Device(PaginatedAPIMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    device_type = db.Column(db.String(32))
    comment = db.Column(db.String(256))
    date_reg = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    data = db.relationship('Data', backref='device', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def from_dict(self, data, new_device=False):
        for field in ['name','device_type', 'comment', 'date_reg']:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        data = {
            'device_id': self.id,
            'name': self.name,
            'device_type': self.device_type,
            'comment': self.comment,
            'date_reg': self.date_reg,
            'owner': self.owner.username,

        }
        return data

    def __repr__(self):
        return '<Device {}>'.format(self.name)
#data input   
class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(64))
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    
    def from_dict(self, data):
        for field in ['value','date']:
            if field in data:
                setattr(self, field, data[field])

    def to_dict(self):
        data = {
            'id': self.id,
            'value': self.value,
            'date': self.date,
            'device_id': self.device_id,

        }
        return data


    def __repr__(self):
        return '<Data {}>'.format(self.value)
    
#gets the ID of the user when they log in
@login.user_loader
def load_user(id):
    return User.query.get(int(id))