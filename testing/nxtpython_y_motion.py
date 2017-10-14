#!/usr/bin/env python3


from ymovement import YMovement


import nxt

brick = nxt.locator.find_one_brick(debug=True)



realport = nxt.motor.PORT_B

print("START")
#motor.debug_info()


xmovement = YMovement(realport, brick)

try:
    while True:
        position = int(input())
        xmovement.set_position(position)
finally:
    xmovement.reset()
#motor.debug_info()
print("END")
