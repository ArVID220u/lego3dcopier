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

    def point_to_supportindex(self, point, width, height):
        index = 0
        for i in range(width):
            for j in range(height):
                if point.x == i and point.y == j:
                    return index
                index += 1
        return -1



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
        # only find the relevant reinforce locations
        # which locations are relevant? 
        # we divide the brick into halves, both in the x and y directions
        # then we claim: we need to reinforce at least once in each half
        # that is, the best way to achive this would be to simply mirror the target_location
        # if that cannot be done, we try other things
        width = 2
        height = 2
        if self.brick == "4x2":
            width = 4
        elif self.brick == "2x4":
            height = 4
        self.reinforce_locations = []
        mirror_point = Point((-1-fetchstudpoint.x + width)%width, (-1-fetchstudpoint.y + height)%height)
        mirror_index = self.point_to_supportindex(mirror_point, width, height)
        if support[mirror_index] == 1:
            self.reinforce_locations.append(self.lower_left + mirror_point)
        else:
            taken_x = False
            taken_y = False
            for i, s in enumerate(support):
                if s == 1 and i != fetchstud:
                    thispoint = self.supportindex_to_point(i)
                    if not taken_x:
                        if width == 2:
                            if thispoint.x != fetchstudpoint.x:
                                taken_x = True
                                self.reinforce_locations.append(self.lower_left + thispoint)
                        else:
                            if thispoint.x // 2 != fetchstudpoint.x // 2:
                                taken_x = True
                                self.reinforce_locations.append(self.lower_left + thispoint)
                    if not taken_y:
                        if height == 2:
                            if thispoint.y != fetchstudpoint.y:
                                taken_y = True 
                                self.reinforce_locations.append(self.lower_left + thispoint)
                        else:
                            if thispoint.y // 2 != fetchstudpoint.y // 2:
                                taken_y = True
                                self.reinforce_locations.append(self.lower_left + thispoint)





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

    # find the nxt brick
    brick = nxt.locator.find_one_brick(debug=setup.debug)

    # create the motorcontrol
    global motorcontrol
    motorcontrol = nxt.motcont.MotCont(brick)
    # start the motorcontrol progrm on the nxt
    motorcontrol.start()

    # create the xmovement, ymovement and zmovement
    global xmovement, ymovement, zmovement
    xmovement = XMovement(brick, setup.xmotor)
    ymovement = YMovement(brick, setup.ymotor)
    zmovement = ZMovement(brick, setup.zmotor)

    # now just execute the build instructions, by moving to the fetch location, then the target location, then the reinforce locations
    for instruction in build_instructions:
        move(instruction.fetch_location)
        #fasten()
        time.sleep(5)
        move(instruction.target_location, holdingbrick=True)
        #fasten(brick=True)
        time.sleep(5)
        for reinforce_location in instruction.reinforce_locations:
            move(reinforce_location)
            #fasten(brick=True)
            time.sleep(5)


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
    global motorcontrol
    if "motorcontrol" in globals():
        motorcontrol.stop()





class XMovement:

    def __init__(self, brick, port):
        self.brick = brick
        self.port = port
        self.motor = nxt.motor.Motor(brick, port)

        # we assume regular position, so it starts at stud 11
        self.current_position = 11

        position11tacho = self.motor.get_tacho().block_tacho_count

        # big gears: 620. Small gears: 1240 Then times three
        position0encoder = position11tacho + 620

        # now, calculate stud distance
        #stud_distance = (position11tacho - position0encoder) / 11
        # mathematically calculated
        stud_distance = 56.25
        position0encoder = position11tacho + 11*stud_distance
        stud_distance = -stud_distance

        # calculate all positions using Encoder value
        self.positions = []
        for x in range(12):
            thisposition = position0encoder + stud_distance * x
            self.positions.append(thisposition)

    def set_position(self, position):
        #self.motor.set_target_encoder(self.positions[position], 60)
        global motorcontrol
        # use the move_to command
        motorcontrol.move_to(self.port, 60, self.positions[position])
        time.sleep(self.approx_duration(position))
        self.current_position = position

    def reset(self):
        # move to regular position, that is, position 15
        self.set_position(11)
        # also move a bit more, since we want to be sure to reset
        #self.motor.set_target_encoder(self.positions[position].plus(-100), 100)

    def approx_duration(self, positionto):
        # speed approximately 4 studs per second
        return abs(self.current_position - positionto)/4*10



class YMovement:

    def __init__(self, brick, port):
        self.brick = brick
        self.port = port
        self.motor = nxt.motor.Motor(brick, port)

        # we assume regular position, so it starts at stud 18
        self.current_position = 18

        position19tacho = self.motor.get_tacho().block_tacho_count

        # with small gears: multiply by 2
        position0tacho = position19tacho - 1070*2

        # now, calculate stud distance
        #stud_distance = (position19tacho - position0tacho) / 18
        # mathematically calculated
        stud_distance = 112.5
        position0tacho = position19tacho - 19*stud_distance

        # calculate all positions using Encoder value
        self.positions = []
        for x in range(20):
            thisposition = position0tacho + stud_distance * x
            self.positions.append(thisposition)

    def set_position(self, position):
        #self.motor.set_target_encoder(self.positions[position], 60)
        global motorcontrol
        # use the move_to command
        motorcontrol.move_to(self.port, 60, self.positions[position])
        time.sleep(self.approx_duration(position))
        self.current_position = position

    def reset(self):
        # move to regular position, that is, position 15
        self.set_position(18)
        # also move a bit more, since we want to be sure to reset
        #self.motor.set_target_encoder(self.positions[position].plus(-100), 100)

    def approx_duration(self, positionto):
        # speed approximately 4 studs per second
        return abs(self.current_position - positionto)/4*10


class ZMovement:

    def __init__(self, brick, port):
        self.brick = brick
        self.port = port
        self.motor = nxt.motor.Motor(brick, port)

        # we assume regular position, so it starts at stud 3
        self.current_position = 3

        position3tacho = self.motor.get_tacho().block_tacho_count

        # MEASURE CORRECT VALUE
        self.position0tacho = position3tacho - 3180

        # now, calculate stud distance
        self.stud_distance = (position3tacho - self.position0tacho) / 3


    def set_position(self, position):
        if position == self.current_position:
            return
        #self.motor.set_target_encoder(self.position0tacho.plus(self.stud_distance * position), 120, brake=False)
        global motorcontrol
        motorcontrol.move_to(self.port, self.position0tacho + self.stud_distance * position, 100)
        time.sleep(self.approx_duration(position))
        self.current_position = position

    def reset(self):
        # move to regular position, that is, position 3
        # first move up to position 4, though
        self.set_position(4)
        self.set_position(3)
        # also move a bit more, since we want to be sure to reset
        #self.motor.set_target_encoder(self.positions[position].plus(-100), 100)

    def approx_duration(self, positionto):
        # speed approximately 1 stud per second
        return abs(self.current_position - positionto)*10


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
    else:
        zmovement.motor.turn(-120, 200)
    time.sleep(1)
    zmovement.set_position(zmovement.current_position)
