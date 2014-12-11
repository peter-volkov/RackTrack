#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import time
import json

GPIO.setwarnings(False)

def read_unit_state(unit_number):
    MIFAREReader = MFRC522.MFRC522(dev='/dev/spidev0.{0}'.format(unit_number))

    # Scan for cards    
    status, TagType = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    if status == MIFAREReader.MI_OK:
        status, uid = MIFAREReader.MFRC522_Anticoll()
        return uid    

while True:
    for unit_number in [0, 1]:
       object_id = read_unit_state(unit_number)
       if object_id:
           print('Unit {0} contains object {1}'.format(unit_number, object_id))
       else:
           print('Unit {0} contains no object'.format(unit_number))
       time.sleep(1)

