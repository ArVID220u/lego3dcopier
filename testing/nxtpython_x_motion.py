#!/usr/bin/env python3

from xmovement import XMovement


import nxt

brick = nxt.locator.find_one_brick(debug=True)



realport = nxt.motor.PORT_A

print("START")
#motor.debug_info()


xmovement = XMovement(realport, brick)

try:
    while True:
        position = int(input())
        xmovement.set_position(position)
finally:
    xmovement.reset()
#motor.debug_info()
print("END")
