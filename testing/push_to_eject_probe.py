#!/usr/bin/env python3

from BrickPi import *

BrickPiSetup()

touch = PORT_3
motor1 = PORT_C

BrickPi.MotorEnable[motor1] = 1

BrickPi.SensorType[touch] = TYPE_SENSOR_TOUCH

BrickPiSetupSensors()

while True:
    result = BrickPiUpdateValues()

    if not result:
        if BrickPi.Sensor[touch]:
            BrickPi.MotorSpeed[motor1] = 200
        else:
            BrickPi.MotorSpeed[motor1] = -200

    print("degrees: " + str(BrickPi.Encoder[motor1]))

    time.sleep(0.1)
