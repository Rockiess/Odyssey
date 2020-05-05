# -*- coding: utf-8 -*-
"""
Created on Fri May  1 13:17:41 2020

@author: redba
"""

from flask import Blueprint

bp = Blueprint('errors', __name__)

from app.errors import handlers