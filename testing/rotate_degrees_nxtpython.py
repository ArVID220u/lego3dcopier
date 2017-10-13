#!/usr/bin/env python3

import nxt

brick = nxt.locator.find_one_brick(debug=True)

port = input("port: ").lower().strip()

realport = nxt.motor.PORT_A
if port == "b":
    realport = nxt.motor.PORT_B
elif port == "c":
    realport = nxt.motor.PORT_C

motor = nxt.motor.Motor(brick, realport)

degrees = int(input())
speed = 127
if degrees < 0:
    speed = -128
    degrees = -degrees

motor.turn(speed, degrees)
