#!/usr/bin/env python3

import nxt
import setup
import time

class Point:
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.z = z
    def __add__(self, p):
        return Point(self.x + p.x, self.y + p.y, self.z + p.z)


class NoSupportException(Exception):
    pass




# the locations for fetching bricks
fetch_2x2 = Point(5,16,2/3)
fetch_4x2 = Point(0,16,2/3)
fetch_2x4_1 = Point(8,16,2/3)
fetch_2x4_2 = Point(10,16,2/3)
fetch_2x4_1_active = True

def fetch_location(brick):
    if brick == "2x2":
        global fetch_2x2
        return fetch_2x2
    if brick == "4x2":
        global fetch_4x2
        return fetch_4x2
    if brick == "2x4":
        global fetch_2x4_1_active
        if fetch_2x4_1_active:
            global fetch_2x4_1
            fetch_2x4_1_active = False
            return fetch_2x4_1
        else:
            global fetch_2x4_2
            fetch_2x4_1_active = True
            return fetch_2x4_2



# The instruction class for the building instructions
class Instruction:

    
    def supportindex_to_point(self, index):
        if self.brick == "2x2":
            for i in range(2):
                for j in range(2):
                    if index == 0:
                        return Point(i, j)
                    index -= 1
        elif self.brick == "2x4":
            for i in range(2):
                for j in range(4):
                    if index == 0:
                        return Point(i, j)
                    index -= 1
        elif self.brick == "4x2":
            for i in range(4):
                for j in range(2):
                    if index == 0:
                        return Point(i, j)
                    index -= 1


    def __init__(self, brick, x, y, z, support):
        self.lower_left = Point(x, y, z)
        self.brick = brick
        self.support = support

        # find the fetch and target location
        fetchstud = -1
        # try to make it as median as possible, if 4x2 or 2x4 brick
        if self.brick == "4x2":
            # therefore, start at index 2, and take the first 1
            for i in range(2,8):
                if support[i] == 1:
                    fetchstud = i
                    break
        elif self.brick == "2x4":
            # check index 1, 2, 5, 6
            accept_index = [1, 2, 5, 6]
            for i in accept_index:
                if support[i] == 1:
                    fetchstud = i
                    break
        if fetchstud == -1:
            for i, s in enumerate(support):
                if s == 1:
                    fetchstud = i
                    break
        if fetchstud == -1:
            # raise exception!!!
            raise NoSupportException()
        
        fetchstudpoint = self.supportindex_to_point(fetchstud)
        
        # now convert this fetchstud into one fetch location and one target location
        self.target_location = self.lower_left + fetchstudpoint
        # the fetch location is the
        self.fetch_location = fetch_location(self.brick) + fetchstudpoint


        # find the reinforce locations
        self.reinforce_locations = []
        for i, s in enumerate(support):
            if s == 1 and i != fetchstud:
                self.reinforce_locations.append(self.lower_left + self.supportindex_to_point(i))


def current_point():
    global xmovement, ymovement, zmovement
    return Point(xmovement.current_position, ymovement.current_position, zmovement.current_position)

def build(legotile_output):
    # convert the legotile_output to build instructions
    # the build instructions will be a list of build_instructions from the printer
    build_instructions = []
    for line in legotile_output.strip().split("\n"):
        rawinstruction = line.strip().split(" ")
        instruction = Instruction(brick=rawinstruction[0], x=int(rawinstruction[1]), y=int(rawinstruction[2]), z=int(rawinstruction[3]), support=[int(x) for x in rawinstruction[4:]])
        build_instructions.append(instruction)


    # create the xmovement, ymovement and zmovement
    global xmovement, ymovement, zmovement
    brick = nxt.locator.find_one_brick(debug=setup.debug)
    xmovement = XMovement(brick, setup.xmotor)
    ymovement = YMovement(brick, setup.ymotor)
    zmovement = ZMovement(brick, setup.zmotor)

    # now just execute the build instructions, by moving to the fetch location, then the target location, then the reinforce locations
    for instruction in build_instructions:
        move(instruction.fetch_location)
        fasten()
        move(instruction.target_location, holdingbrick=True)
        fasten(brick=True)
        for reinforce_location in instruction.reinforce_locations:
            move(reinforce_location)
            fasten(brick=True)


def move(point, holdingbrick=False):
    addheight = 0
    if holdingbrick:
        addheight = 1
    zmovement.set_position(max(max(point.z, current_point().z), 2) + addheight)
    xmovement.set_position(point.x)
    ymovement.set_position(point.y)
    time.sleep(1)
    zmovement.set_position(point.z)


def reset():
    global xmovement, ymovement, zmovement
    if "zmovement" in globals():
        zmovement.reset()
    if "ymovement" in globals():
        ymovement.reset()
    if "xmovement" in globals():
        xmovement.reset()





class XMovement:

    def __init__(self, brick, port):
        self.brick = brick
        self.port = port
        self.motor = nxt.motor.Motor(brick, port)

        # we assume regular position, so it starts at stud 11
        self.current_position = 11

        position11tacho = self.motor.get_tacho()

        position0encoder = position11tacho.plus(620)

        # now, calculate stud distance
        stud_distance = (position11tacho.plus(-position0encoder.tacho_count)).tacho_count / 11

        # calculate all positions using Encoder value
        self.positions = []
        for x in range(12):
            thisposition = position0encoder.plus(stud_distance * x)
            self.positions.append(thisposition)

    def set_position(self, position):
        self.motor.set_target_encoder(self.positions[position], 60)
        self.current_position = position

    def reset(self):
        # move to regular position, that is, position 15
        self.set_position(11)
        # also move a bit more, since we want to be sure to reset
        #self.motor.set_target_encoder(self.positions[position].plus(-100), 100)



class YMovement:

    def __init__(self, brick, port):
        self.brick = brick
        self.port = port
        self.motor = nxt.motor.Motor(brick, port)

        # we assume regular position, so it starts at stud 18
        self.current_position = 18

        position19tacho = self.motor.get_tacho()

        position0tacho = position19tacho.plus(-1070)

        # now, calculate stud distance
        stud_distance = (position19tacho.plus(-position0tacho.tacho_count)).tacho_count / 18

        # calculate all positions using Encoder value
        self.positions = []
        for x in range(20):
            thisposition = position0tacho.plus(stud_distance * x)
            self.positions.append(thisposition)

    def set_position(self, position):
        self.motor.set_target_encoder(self.positions[position], 60)
        self.current_position = position

    def reset(self):
        # move to regular position, that is, position 15
        self.set_position(18)
        # also move a bit more, since we want to be sure to reset
        #self.motor.set_target_encoder(self.positions[position].plus(-100), 100)


class ZMovement:

    def __init__(self, brick, port):
        self.brick = brick
        self.port = port
        self.motor = nxt.motor.Motor(brick, port)

        # we assume regular position, so it starts at stud 3
        self.current_position = 3

        position3tacho = self.motor.get_tacho()

        # MEASURE CORRECT VALUE
        self.position0tacho = position3tacho.plus(-3180)

        # now, calculate stud distance
        self.stud_distance = (position3tacho.plus(-self.position0tacho.tacho_count)).tacho_count / 3


    def set_position(self, position):
        if position == self.current_position:
            return
        self.motor.set_target_encoder(self.position0tacho.plus(self.stud_distance * position), 120, brake=False)
        self.current_position = position

    def reset(self):
        # move to regular position, that is, position 3
        # first move up to position 4, though
        self.set_position(4)
        self.set_position(3)
        # also move a bit more, since we want to be sure to reset
        #self.motor.set_target_encoder(self.positions[position].plus(-100), 100)


def fasten(brick=False):
    # lower with 30 pts, then move in x and y directions, then lower with 20 pts, then move...
    # do this 5 times
    import time
    time.sleep(3)
    zmovement.motor.set_target_encoder(zmovement.motor.get_tacho().plus(-500), 120, brake=False)
    for i in range(3,6):
        #zmovement.motor.set_target_encoder(zmovement.motor.get_tacho().plus(-100), 120, brake=False)
        zmovement.motor.turn(-120, 100, brake=False)
        xmovement.motor.turn(60, 20)
        time.sleep(0.5)
        ymovement.motor.turn(60, 20)
        time.sleep(0.5)
        xmovement.motor.turn(-60, 50)
        time.sleep(0.5)
        ymovement.motor.turn(-60, 40)
        time.sleep(0.5)
        xmovement.set_position(xmovement.current_position)
        ymovement.set_position(ymovement.current_position)
        time.sleep(1)
    # now push
    #zmovement.motor.set_target_encoder(zmovement.motor.get_tacho().plus(-500), 120, brake=False)
    if brick:
        zmovement.motor.turn(-120, 1500)
    zmovement.set_position(zmovement.current_position)
