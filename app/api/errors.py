# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 16:07:08 2020

@author: redba
"""

from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES

def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response
    pass

def bad_request(message):
    return error_response(400, message)

