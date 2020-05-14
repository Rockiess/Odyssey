# -*- coding: utf-8 -*-
"""
Created on Wed May 13 13:33:50 2020

@author: redba
"""

from app.models import Device, Data, User
from datetime import timedelta, datetime, timezone

#From a given device, returns "value" and "date" data logged for the last "time" in seconds 
def returnChartVal (device, time):
    data = device.data.filter(Data.date > timedelta(seconds=-time)).all()
    values = []
    time = []
    for i in data:
        values.append(i.value)
        time.append(i.date.replace(tzinfo=timezone.utc).astimezone(tz=None).strftime("%a %I:%M %p"))
        
    return values, time

    
    


    
        
    
    