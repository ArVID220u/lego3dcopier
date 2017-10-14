#!/usr/bin/env python3

from xmovement import XMovement
from ymovement import YMovement


import nxt

brick = nxt.locator.find_one_brick(debug=True)



xport = nxt.motor.PORT_A
yport = nxt.motor.PORT_B

print("START")
#motor.debug_info()


x = XMovement(xport, brick)
y = YMovement(yport, brick)



try:
    while True:
        xpos, ypos = [int(x) for x in input().split()]
        x.set_position(xpos)
        y.set_position(ypos)
finally:
    x.reset()
    y.reset()
#motor.debug_info()
print("END")
