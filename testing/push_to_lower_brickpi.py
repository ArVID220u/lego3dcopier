#!/usr/bin/env python3

import BrickPi as bp
import time

bp.BrickPiSetup()

touch = bp.PORT_3
motor = bp.PORT_D

bp.BrickPi.SensorType[touch] = bp.TYPE_SENSOR_TOUCH

bp.BrickPiSetupSensors()


class Height:
    def __init__(self, port):
        self.port = port
        bp.BrickPiUpdateValues()
        self.height1 = bp.BrickPi.Encoder[self.port]
        # assume position is something
        # 500 equals 90 degrees
        self.height2 = self.height1 - 500

    def toggle(self):
        bp.BrickPi.MotorEnable[self.port] = 1
        bp.BrickPiUpdateValues()
        cur_enc = bp.BrickPi.Encoder[self.port]
        if abs(cur_enc - self.height1) < abs(cur_enc - self.height2):
            bp.set_target_encoder(self.port, self.height2, 150)
        else:
            bp.set_target_encoder(self.port, self.height1, 150)
        bp.BrickPi.MotorEnable[self.port] = 0
        bp.BrickPiUpdateValues()
        bp.debug_out("encoder: " + str(bp.BrickPi.Encoder[self.port]))

height = Height(motor)

while True:
    result = bp.BrickPiUpdateValues()

    if not result:
        if bp.BrickPi.Sensor[touch]:
            # rotate
            height.toggle()

    time.sleep(0.1)
