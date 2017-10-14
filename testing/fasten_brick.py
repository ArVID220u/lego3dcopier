#!/usr/bin/env python3

import nxt

brick = nxt.locator.find_one_brick(debug=True)

port = nxt.motor.PORT_C

motor = nxt.motor.Motor(brick, port)
xmotor = nxt.motor.Motor(brick, nxt.motor.PORT_A)
ymotor = nxt.motor.Motor(brick, nxt.motor.PORT_B)

start_tacho = motor.get_tacho()
xmotor_start = xmotor.get_tacho()
ymotor_start = ymotor.get_tacho()

import time

try:

    # lower with 30 pts, then move in x and y directions, then lower with 20 pts, then move...
    # do this 5 times
    motor.set_target_encoder(motor.get_tacho().plus(-150), 120, recurse=False)
    for i in range(3,10):
        motor.set_target_encoder(motor.get_tacho().plus(-30), 120, recurse=False)
        xmotor.turn(100, 20*i/5)
        ymotor.turn(100, 20*i/5)
        xmotor.turn(-100, 40*i/5)
        ymotor.turn(-100, 40*i/5)
        xmotor.set_target_encoder(xmotor_start, 100)
        ymotor.set_target_encoder(ymotor_start, 100)
    # now push
    motor.set_target_encoder(motor.get_tacho().plus(-500), 120, recurse=False)


finally:
    motor.set_target_encoder(start_tacho.plus(500), 120, recurse=False)
    time.sleep(0.5)
    motor.set_target_encoder(start_tacho, 120)
    xmotor.set_target_encoder(xmotor_start, 100)
    ymotor.set_target_encoder(ymotor_start, 100)
