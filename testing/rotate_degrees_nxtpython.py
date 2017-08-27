#!/usr/bin/env python3

import nxt

brick = nxt.locator.find_one_brick(debug=True)

motor = nxt.motor.Motor(brick, nxt.motor.PORT_A)

degrees = int(input())

motor.turn(80, degrees)
