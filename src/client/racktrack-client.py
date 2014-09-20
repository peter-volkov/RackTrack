#!/usr/bin/env python
# -*- coding: utf8 -*-

import json
import logging
import signal
import time
import urllib
import urllib2

import RPi.GPIO as GPIO
import MFRC522
from ds18b20 import DS18B20

continue_reading = True
temperature_sensor = DS18B20()

racktrack_servers = ['192.168.1.1', 'racktrack.ru']
plugged_blade_servers = {}
num_units = 42

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."

rack_notification = {"meta": {"racktrack_client_version": 0.1, "rack_id": '1.12.4', "num_units": 42}, 
                     "temperature_info": {"back_sensors": {}, "front_sensors": {}}, 
                     "plugged_blade_servers": {}
                    }

def send_notifictaion(rack_notification):
    notification = {'data': json.dumps(rack_notification)}
    post_data = urllib.urlencode(notification) 
    
    for hostname in racktrack_servers:
        req = urllib2.Request('https://{0}/data-receiver/'.format(hostname), post_data, headers) 
        try:
            response = urllib2.urlopen(req)
        except Exception as ex:
            print(ex)

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:

    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    time.sleep(1)
    print(json.dumps({'status': status, 'TagType': TagType}))
    
    # If a card is found
    if status == MIFAREReader.MI_OK:
        status, uid = MIFAREReader.MFRC522_Anticoll()    
        rack_notification["plugged_blade_servers"]["uid"] = 1         
    
    temperature_in_celsius = temperature_sensor.get_temperature()
    rack_notification["temperature_info"]["back_sensors"]["top"] = temperature_in_celsius
    send_notifictaion(rack_notification)
    
