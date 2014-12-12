#!/usr/bin/env python
# -*- coding: utf8 -*-

import urllib
import urllib2
import argparse
import time
import json

import RPi.GPIO as GPIO
import MFRC522
from ds18b20 import DS18B20

GPIO.setwarnings(False)

class RackTrackServerClient:
    def __init__(self, rack_id):
        self.rack_id = rack_id

        self.server_host = "racktrack-server.ml"

        self.move_object_url = "http://{}/index.php?module=redirect&page=object&tab=rackspace&op=updateObjectAllocation".format(self.server_host)
        self.temperature_url = "http://{}/index.php?module=redirect&page=rack&tab=temperature&op=updateRackTemperature".format(self.server_host)

        #rack objects are servers, network equipment and anything else, that could be installed
        #  into ther ack and needs inventarization

        #rack object are pairs, where key is a unit_number and value is a object id
        self.rack_objects = {1: '7de2d2b5f8', 2: 'e324dbc7db'}

        self.http_headers = {
           'Authorization': 'Basic YWRtaW46cm9vdA=='
        }

        dallas_sensors = DS18B20()
        self.temperature_sensors = dallas_sensors.get_all_sensors()
        self.sensor_dict = {'000005cf88f3': 'top', '000005cfaaa4': 'middle', '000005cf5953': 'bottom'}
                                                                           
        self.object_dict = {'7de2d2b5f8': '5', 'e324dbc7db': '6', 'e2767d55bc': '7'}

    def _read_unit_state(self, unit_number):
        MIFAREReader = MFRC522.MFRC522(dev='/dev/spidev0.{0}'.format(unit_number - 1))

        # Scan for nfc chips 
        status, TagType = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

        if status == MIFAREReader.MI_OK:
            status, uid = MIFAREReader.MFRC522_Anticoll()
            return ''.join(map(lambda number: hex(number)[2:], uid))    
        
    def send_temperature_info(self):
        
        current_temperature = {}

        for sensor in self.temperature_sensors:
            sensor_name = self.sensor_dict[sensor._id]          
            current_temperature[sensor_name] = sensor.get_temperature()

        temperature_post_data = {
            'rack_id': self.rack_id,
            'top': int(round(current_temperature['top'])),
            'middle': int(round(current_temperature['middle'])),
            'bottom': int(round(current_temperature['bottom'])),
        }

        post_data = urllib.urlencode(temperature_post_data)
        request = urllib2.Request(self.temperature_url, urllib.urlencode(temperature_post_data), self.http_headers)
        print(temperature_post_data)
        return urllib2.urlopen(request).read()

    def send_object_presence_info(self):        
        for unit_number, rack_object_id in self.rack_objects.iteritems():

            move_object_post_data = None
            rack_object_id = self._read_unit_state(unit_number)

            if rack_object_id:
                move_object_post_data = {
                    'object_id': self.object_dict.get(rack_object_id),
                    'rackmulti[]': self.rack_id,
                    'comment': '',
                    'got_atoms': 'Save',
                    'atom_{0}_{1}_0'.format(self.rack_id, unit_number): 'on',
                    'atom_{0}_{1}_1'.format(self.rack_id, unit_number): 'on',
                    'atom_{0}_{1}_2'.format(self.rack_id, unit_number): 'on',
                }
                self.rack_objects[unit_number] = rack_object_id

            elif not rack_object_id and self.rack_objects[unit_number]:            
                move_object_post_data = {
                    'object_id': self.object_dict.get(self.rack_objects[unit_number]),
                    'rackmulti[]': self.rack_id,
                    'comment': '',
                    'got_atoms': 'Save',
                }
                self.rack_objects[unit_number] = None

            if move_object_post_data:
                post_data = urllib.urlencode(move_object_post_data)
                request = urllib2.Request(self.move_object_url, urllib.urlencode(move_object_post_data), self.http_headers)
                print(move_object_post_data)
                urllib2.urlopen(request).read()
              
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="RackTrack  v 0.1")
    parser.add_argument('--rack_id', metavar="<number>", required=True, type=int, help="Rack id number")
    cmd_args = parser.parse_args()

    sender = RackTrackServerClient(cmd_args.rack_id)
    while True:
        sender.send_temperature_info()
        sender.send_object_presence_info()

