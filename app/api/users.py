# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 16:06:33 2020

@author: redba
"""

from app.api import bp
from flask import jsonify
from app.models import User, Device, Data
from flask import request
from flask import url_for
from app import db
from app.api.errors import bad_request
from flask import g, abort
from app.api.auth import token_auth
from datetime import datetime

@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())

@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_user', id=user.id)
    return response

@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    if g.current_user.id != id:
        abort(403)
    user = User.query.get_or_404(id)
    data = request.get_json() or {}
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())

@bp.route('/users/<int:id>/device/', methods=['GET'])
@token_auth.login_required
def get_device(id):
    if g.current_user.id != id:
        abort(403)
    return jsonify(Device.query.get_or_404(id).to_dict())

@bp.route('/users/<int:id>/device', methods=['POST'])
@token_auth.login_required
def create_device(id):
    if g.current_user.id != id:
        abort(403)
    user = User.query.get_or_404(id)
    devices = Device.query.all()
    data = request.get_json() or {}
    if 'name' not in data or 'device_type' not in data:
        return bad_request('must include name and device_type fields')
    #TODO:Find a way to get specific users devices and check for reoccuring names 
    for i in devices:
        if g.current_user == i.owner:
            if i.name == data['name']:
                return bad_request('Please choose a different name')
            
    #Sets owner for device
    device = Device(owner=User.query.get(id))
    device.date_reg = datetime.utcnow()
    #TODO: Set comments for certain device types
    device.comment = 'NA'
    
    device.from_dict(data, new_device=True)
    db.session.add(device)
    db.session.commit()
    response = jsonify(device.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_device', id=user.id)
    return response

@bp.route('/users/<int:u_id>/device/<int:d_id>', methods=['PUT'])
@token_auth.login_required
def update_device(u_id, d_id):
    if g.current_user.id != u_id or Device.query.get(d_id).user_id != g.current_user.id:
        abort(403)
    
    device = Device.query.get_or_404(d_id)
    data = request.get_json() or {}
    #TODO make it so the name actually changes
    if 'name' not in data or 'device_type' not in data:
        return bad_request('must include name name and device_type fields')
   
    device.from_dict(data, new_device=False)
    db.session.commit()
    response = jsonify(device.to_dict())
    return response

@bp.route('/users/<int:id>/devices', methods=['GET'])
@token_auth.login_required
def get_devices(id):
    if g.current_user.id != id:
        abort(403)
        
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Device.to_collection_dict(Device.query.filter_by(user_id=id), page, per_page, 'api.get_users')
    return jsonify(data)


@bp.route('/users/<int:id>/device/<int:d_id>', methods=['GET'])
@token_auth.login_required
def get_data(u_id, d_id):
    if g.current_user.id != u_id:
        abort(403)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Data.to_collection_dict(Data.query.filter_by(device_id=d_id), page, per_page, 'api.get_users')
    return jsonify(data)


@bp.route('/users/<int:u_id>/device/<int:d_id>/send', methods=['POST'])
@token_auth.login_required
def log_data(u_id, d_id):
    if g.current_user.id != u_id or Device.query.get(d_id).user_id != g.current_user.id:
        abort(403)

    data = request.get_json() or {}

    if 'value' not in data:
        return bad_request('must include a value')
    
    logging = Data(device=Device.query.get(d_id))
    logging.date = datetime.utcnow()
    logging.from_dict(data)
    db.session.add(logging)
    db.session.commit()
    response = jsonify(logging.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_device', id=u_id)

    return response
