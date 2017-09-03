#!/usr/bin/env python3

import BrickPi as bp
import time

bp.BrickPiSetup()

touch = bp.PORT_4
motor = bp.PORT_B

bp.BrickPi.SensorType[touch] = bp.TYPE_SENSOR_TOUCH

bp.BrickPiSetupSensors()


class Rotation:
    def __init__(self, port):
        self.port = port
        bp.BrickPiUpdateValues()
        self.positions = []
        for i in range(4):
            # one revolution is 720 units
            # 14 revolutions are needed for a 90 degree turn
            self.positions.append(bp.BrickPi.Encoder[self.port] + i*14*720)
        self.current_position = 0

    def set_position(self, position):
        bp.BrickPi.MotorEnable[self.port] = 1
        bp.BrickPiUpdateValues()
        cur_enc = bp.BrickPi.Encoder[self.port]
        bp.set_target_encoder(self.port, self.positions[position], 200)
        bp.BrickPi.MotorEnable[self.port] = 0
        bp.BrickPiUpdateValues()
        self.current_position = position
        bp.debug_out("encoder: " + str(bp.BrickPi.Encoder[self.port]))

    def next_position(self):
        self.set_position((self.current_position + 1)%4)

rotation = Rotation(motor)

while True:
    result = bp.BrickPiUpdateValues()

    if not result:
        if bp.BrickPi.Sensor[touch]:
            # rotate
            rotation.next_position()

    time.sleep(0.1)
