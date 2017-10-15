#!/usr/bin/env python3

import nxt
import time

brick = nxt.locator.find_one_brick(debug=True)

port = input("port: ").lower().strip()


realport = nxt.motor.PORT_A
if port == "b":
    realport = nxt.motor.PORT_B
elif port == "c":
    realport = nxt.motor.PORT_C

motor = nxt.motor.Motor(brick, realport)

print("START")
motor.debug_info()

degrees = int(input())

target = motor.get_tacho().get_target(degrees)

motor.set_target_encoder(target, 100, brake=(port != "c")) 
"""motor.turn(120,degrees)
time.sleep(3)
motor.turn(100,degrees)
time.sleep(3)
motor.turn(80,degrees)
time.sleep(3)
motor.turn(60,degrees)
time.sleep(3)
motor.turn(40,degrees)
time.sleep(3)
motor.turn(20,degrees)
time.sleep(3)"""
#motor.turn(60,degrees)
#motor.set_target_encoder(target, 60)

motor.debug_info()
print("END")
