#!/usr/bin/env python3

# setup file

debug = True

# SCANNER
import BrickPi as bp

start_button_port = bp.PORT_3
rotate_base_port = bp.PORT_A
slide_probe_port = bp.PORT_B
eject_probe_port = bp.PORT_C
lower_object_port = bp.PORT_D
probe_sensor_port = bp.PORT_1



# LEGOTILE ALGORITHM
legotile_algorithm_executable = "legotile"



# PRINTER
import nxt
xmotor = nxt.motor.PORT_A
ymotor = nxt.motor.PORT_B
zmotor = nxt.motor.PORT_C
