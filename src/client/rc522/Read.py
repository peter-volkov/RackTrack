#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
import time
import json

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
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

no_mark_number = 0

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:

    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    time.sleep(0.1)
    #print(json.dumps({'status': status ,'TagType': TagType}))
    
    # If a card is found
    if status == MIFAREReader.MI_OK:        
        (status,uid) = MIFAREReader.MFRC522_Anticoll()
        #[178, 122, 144, 181, 237] -> b2:7a:90:b5:ed
        hex_uid = ':'.join(map(lambda number: hex(number)[2:], uid))
        if no_mark_number > 3:
            print("Mark {0} detected".format(hex_uid))
        no_mark_number = 0
    else:
        if no_mark_number == 3:
            print('no mark')
            no_mark_number += 1
        else:
            no_mark_number += 1
    # Get the UID of the card
    #(status,uid) = MIFAREReader.MFRC522_Anticoll()
    #print(json.dumps({'status': status ,'uid': uid}))
    continue

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Print UID
        print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
    
        # This is the default key for authentication
        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            MIFAREReader.MFRC522_Read(8)
            MIFAREReader.MFRC522_StopCrypto1()
        else:
            print "Authentication error"

