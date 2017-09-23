#!/usr/bin/env python3

import BrickPi as brickpi
#from set_encoder_brickpi import set_target_encoder

brickpi.BrickPiSetup()

motor = brickpi.PORT_A

brickpi.BrickPi.MotorEnable[motor] = 1
brickpi.BrickPiUpdateValues()
startencoder = brickpi.BrickPi.Encoder[motor]
print("degrees: " + str(brickpi.BrickPi.Encoder[motor]))

degree = int(input())

brickpi.set_target_encoder(motor, brickpi.BrickPi.Encoder[motor] + degree * 2, 200)
print("degrees: " + str(brickpi.BrickPi.Encoder[motor]))
endencoder = brickpi.BrickPi.Encoder[motor]

print("realdegrees: " + str((endencoder - startencoder)/2))
