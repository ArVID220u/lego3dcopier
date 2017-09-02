#!/usr/bin/env python3

import BrickPi as brickpi

brickpi.BrickPiSetup()

motor = brickpi.PORT_B

brickpi.BrickPi.MotorEnable[motor] = 1

import time
while True:
    brickpi.BrickPiUpdateValues()
    print("degrees: " + str(brickpi.BrickPi.Encoder[motor]))
    time.sleep(3)


