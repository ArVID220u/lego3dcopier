#!/usr/bin/env python3

from BrickPi import *

BrickPiSetup()

touch = PORT_3
motor1 = PORT_B

BrickPi.MotorEnable[motor1] = 1

BrickPi.SensorType[touch] = TYPE_SENSOR_TOUCH

BrickPiSetupSensors()

while True:
    result = BrickPiUpdateValues()

    if not result:
        if BrickPi.Sensor[touch]:
            set_target_encoder(motor1, BrickPi.Encoder[motor1] + 110, 150)
        else:
            set_target_encoder(motor1, BrickPi.Encoder[motor1] - 110, 150)

    print("degrees: " + str(BrickPi.Encoder[motor1]))

    time.sleep(1)
