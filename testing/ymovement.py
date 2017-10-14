#!/usr/bin/env python3
import nxt
class YMovement:

    def __init__(self, port, brick):
        self.brick = brick
        self.port = port
        self.motor = nxt.motor.Motor(brick, port)

        # we assume regular position, so it starts at stud 19
        self.current_position = 19

        position19tacho = self.motor.get_tacho()

        position0tacho = position19tacho.plus(-1070)

        # now, calculate stud distance
        stud_distance = (position19tacho.plus(-position0tacho.tacho_count)).tacho_count / 19

        self.current_position = 0

        # calculate all positions using Encoder value
        self.positions = []
        for x in range(20):
            thisposition = position0tacho.plus(stud_distance * x)
            self.positions.append(thisposition)

    def set_position(self, position):
        self.motor.set_target_encoder(self.positions[position], 100)
        self.current_position = position

    def reset(self):
        # move to regular position, that is, position 15
        self.set_position(19)
        # also move a bit more, since we want to be sure to reset
        #self.motor.set_target_encoder(self.positions[position].plus(-100), 100)
