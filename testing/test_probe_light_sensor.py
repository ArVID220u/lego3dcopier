#!/usr/bin/env python3


import BrickPi as bp
import time

bp.BrickPiSetup()  # setup the serial port for communication

color = bp.PORT_1

#col = [None , "Black","Blue","Green","Yellow","Red","White" ]   #used for converting the color index to name

bp.BrickPi.SensorType[color] = bp.TYPE_SENSOR_COLOR_RED

bp.BrickPiSetupSensors()

inn = False
while True:
    result = bp.BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors 
    if not result:
        val = bp.BrickPi.Sensor[color]     #BrickPi.Sensor[PORT] stores the value obtained from sensor
        if val > 110 and not inn:
            inn = True
            print("In!")
        if val < 90 and inn:
            inn = False
            print("Out!")
    time.sleep(.1)     # sleep for 100 m
