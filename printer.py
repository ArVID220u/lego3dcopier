#!/usr/bin/env python3


class Point:
    def __init__(x, y, z=0):
        self.x = x
        self.y = y
        self.z = z
    def __add__(self, p):
        return Point(self.x + p.x, self.y + p.y, self.z + p.z)


class NoSupportException(Exception):
    pass




# the locations for fetching bricks
fetch_2x2 = Point(5,16,1+2/3)
fetch_4x2 = Point(0,16,1+2/3)
fetch_2x4_1 = Point(8,16,1+2/3)
fetch_2x4_2 = Point(10,16,1+2/3)
fetch_2x4_1_active = True

def fetch_location(brick):
    if brick == "2x2":
        return fetch_2x2
    if brick == "4x2":
        return fetch_4x2
    if brick == "2x4":
        if fetch_2x4_1_active:
            fetch_2x4_1_active = False
            return fetch_2x4_1
        else:
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

def build(legotile_output):
    # convert the legotile_output to build instructions
    # the build instructions will be a list of build_instructions from the printer
    build_instructions = []
    for line in legotile_output.strip().split("\n"):
        rawinstruction = line.strip().split(" ")
        instruction = Instruction(brick=rawinstruction[0], x=int(rawinstruction[1]), y=int(rawinstruction[2]), z=int(rawinstruction[3]), support=[int(x) for x in rawinstruction[4:]])
        build_instructions.append(instruction)


    # create the xmovement, ymovement and zmovement
    xmovement = XMovement()
    ymovement = YMovement()
    zmovement = ZMovement()

    # now just execute the build instructions, by moving to the fetch location, then the target location, then the reinforce locations
    for instruction in build_instructions:
        move(instruction.fetch_location)
        fasten()
        move(instruction.target_location)
        fasten()
        for reinforce_location in instruction.reinforce_locations:
            move(reinforce_location)


def move(point):
    # if 


def reset():
    xmovement.reset()
    ymovement.reset()
    zmovement.reset()
