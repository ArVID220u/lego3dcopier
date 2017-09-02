#!/usr/bin/env python3

from BrickPi import *

BrickPiSetup()

touch = PORT_4
motor1 = PORT_B
motor2 = PORT_D

BrickPi.MotorEnable[motor1] = 1
BrickPi.MotorEnable[motor2] = 1

BrickPi.SensorType[touch] = TYPE_SENSOR_TOUCH

BrickPiSetupSensors()

while True:
    result = BrickPiUpdateValues()

    if not result:
        if BrickPi.Sensor[touch]:
            BrickPi.MotorSpeed[motor1] = 150
            BrickPi.MotorSpeed[motor2] = -200
        else:
            BrickPi.MotorSpeed[motor1] = 0
            BrickPi.MotorSpeed[motor2] = 0

    print("degrees: " + str(BrickPi.Encoder[motor1]))

    time.sleep(0.1)
