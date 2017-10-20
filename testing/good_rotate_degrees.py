#!/usr/bin/env python3

import nxt
import time

brick = nxt.locator.find_one_brick(debug=True)

mc = nxt.motcont.MotCont(brick)

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
speed = 80
if degrees < 0:
    speed = -speed
    degrees = -degrees

try:
    mc.start()
    mc.cmd(realport, speed, degrees)


    print("begin sleep")
    time.sleep(abs(degrees))
    print("end sleep")
finally:
    mc.stop()

motor.debug_info()
print("END")
