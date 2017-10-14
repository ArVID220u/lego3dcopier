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

state = motor._get_new_state()

print("START")
motor.debug_info()


tacho = int(input())

state.tacho_limit = tacho
state.power = 127
motor._set_state(state)

motor.debug_info()
print("END")
import time
time.sleep(10)
motor.brake()
