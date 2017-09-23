#!/usr/bin/env python3

# This scanner file implements one function, scan()
# It scans the entire object and returns a 12 by 12 by 19 matrix of 1s and 0s indicating where there are (not) lego bricks present
# -1 in the matrics indicates that we cannot know whether there's a lego brick in that position (i.e. it's shielded in all four directions)
# It assumes that all scanner parts are in regular position

import BrickPi as bp
import setup
import time


def scan():
    # We scan the structure layer by layer
    # Each layer originally consists of a 12 by 12 matrix of -1s
    # Every time we move the probe through a position, we set it to 0 in the matrix, and every time we encounter a stop, we set it to 1
    # Easy

    # First, set up brickpi
    bp.BrickPiSetup()



    # the matrix to return
    # a position is accessed by matrix3d[z][x][y] where z is height
    matrix3d = []

    # eh, I miss c++ here. should I convert to c++? No.

    # create a height object, which assumes regular position, and can lower the object stud by stud
    height = Height(setup.lower_object_port)

    # create a rotation object, which assumes regular position, and can rotate the object in all directions
    rotation = Rotation(setup.rotate_base_port)

    # now eject the probe until stopped by the color sensor (only to level 11)
    ymovement = YMovement(setup.eject_probe_port, setup.probe_sensor_port)

    # don't stop scanning immediately
    stop_scanning = False

    # iterate over each layer
    for z in range(19):

        # let w be the width
        w = 12

        layer = []
        # initialize the layer with -1s
        for x in range(w):
            row = [-1 for y in range(w)]
            layer.append(row)


        if not stop_scanning:

            # now, simply scan from each direction
            for direction in range(4):

                # here, we scan!
                # the x coordinate is along slide_probe axis, increasing to right
                # the y coordinate is along eject_probe axis, increasing away from probe

                bp.BrickPi.MotorEnable[setup.slide_probe_port] = 1
                bp.set_target_encoder(setup.slide_probe_port, bp.BrickPi.Encoder[setup.slide_probe_port] - 60, 150)
                ymovement.calibrate()
                bp.BrickPi.MotorEnable[setup.slide_probe_port] = 0

                # the slide probe assumes regular position
                xmovement = XMovement(setup.slide_probe_port)

                for x in range(w):
                    # we cannot scan the x=0, but since that is unnecessary, it's not a problem
                    if x == 0:
                        continue
                    # set xmovement position
                    print(x)
                    xmovement.set_position(x)
                    
                    # get the endpos
                    endpos = ymovement.find_first_block()
                    # endpos is -1 if no brick is found
                    if endpos == -1:
                        for y in range(w):
                            layer[x][y] = 0
                    else:
                        # set all before to 0, and the endpos to 1
                        if endpos > 0:
                            for y in range(endpos):
                                layer[x][y] = 0
                        layer[x][endpos] = 1
                    # halfreset ymovement
                    ymovement.halfreset()
                    # check if abortion
                    check_if_abort(xmovement, rotation, height)



                # full reset the ymvoement
                ymovement.reset()

                # reset the xmovement; i.e. move the slide probe to regular position
                xmovement.reset()

                # remember to rotate the base after scanning a direction
                rotation.next_position()
                
                # also rotate the layer grid 90 degrees in the same direction as the physical rotation (hmm, is that important? i suspect not)
                layer = rotate_layer(layer)

            # check if layer is empty. if that is so, don't scan the rest of the layers
            is_empty = True
            for x in range(w):
                for y in range(w):
                    if layer[x][y] != -1:
                        is_empty = False
            if is_empty:
                stop_scanning = True


        # append the layer to the matrix3d
        matrix3d.append(layer)

        # now lower the object
        height.lower()



def rotate_layer(layer):
    # rotate the layer 90 degrees in positive direction (same as physical rotation)
    # that is, position (0,0) is rotated to (w-1,0)
    # i.e. new x is old y inverted, and new y is old x
    newlayer = []
    w = len(layer)
    for x in range(w):
        row = [-2 for y in range(w)]
        newlayer.append(row)
    for x in range(w):
        for y in range(w):
            newlayer[x][y] = layer[w-1-y][x]
    return newlayer




# The YMovement class, which ejects the probe until a block is found
class YMovement:

    def __init__(self, motor_port, sensor_port):
        self.motor_port = motor_port
        self.sensor_port = sensor_port
        bp.BrickPiUpdateValues()


        # get the regular position
        self.regular_position = bp.BrickPi.Encoder[self.motor_port]

    def calibrate(self):
        # we assume x position is 12, 13 or 14
        # that is, we just move until we get to first stop, and that first stop is position -7
        # Then, the stud distance is roughly 1460
        stud_distance = 1440
        stop_position = self.move_till_stop(foolhardy=True)
        print("stop_position: " + str(stop_position))
        self.positions = []
        for y in range(-7, 11):
            self.positions.append(stop_position + (y + 7) * stud_distance)
        # then reset
        self.reset()

    def find_first_block(self):
        stop_position = self.move_till_stop()
        if stop_position == None:
            return -1
        # find closest position
        closest_dist = 10000
        closest_pos = -1
        for y in range(-7, 11):
            pos = self.positions[y+7]
            dis = abs(pos-stop_position)
            if dis < closest_dist:
                closest_dist = dis
                closest_pos = y
        return closest_pos
    

    # move until color sensor reaches > 105
    def move_till_stop(self, foolhardy=False):
        # set up the color sensor
        bp.BrickPi.SensorType[self.sensor_port] = bp.TYPE_SENSOR_COLOR_RED
        bp.BrickPiSetupSensors()

        # return encoder value of stop
        bp.BrickPi.MotorEnable[self.motor_port] = 1
        bp.BrickPi.MotorSpeed[self.motor_port] = 200
        while True:
            bp.BrickPiUpdateValues()
            print("motorencoder: " + str(bp.BrickPi.Encoder[self.motor_port]))
            color_val = bp.BrickPi.Sensor[self.sensor_port]
            if color_val > 105:
                break
            if not foolhardy:
                print("goal encoder: " + str(self.positions[10 + 7] + 200))
                if bp.BrickPi.Encoder[self.motor_port] > self.positions[10 + 7] + 200:
                    return None
            time.sleep(0.05)

        # turn off color sensor
        bp.BrickPi.SensorType[self.sensor_port] = bp.TYPE_SENSOR_COLOR_NONE
        bp.BrickPiSetupSensors()

        bp.BrickPi.MotorEnable[self.motor_port] = 0
        bp.BrickPiUpdateValues()
        return bp.BrickPi.Encoder[self.motor_port]
        
    # don't reset for turn, but reset for next scan
    def halfreset(self):
        # move probe to regular position
        bp.BrickPi.MotorEnable[self.motor_port] = 1
        bp.set_target_encoder(self.motor_port, self.positions[5], 200)
        bp.BrickPi.MotorEnable[self.motor_port] = 0

    def reset(self):
        # move probe to regular position
        bp.BrickPi.MotorEnable[self.motor_port] = 1
        bp.set_target_encoder(self.motor_port, self.regular_position, 200)
        bp.BrickPi.MotorEnable[self.motor_port] = 0





# The XMovement class, which slides the probe stud by stud in the x direction
class XMovement:

    def __init__(self, port):
        self.port = port
        bp.BrickPiUpdateValues()

        # we assume regular position, so it starts at stud 14, plus circa 60 units
        self.current_position = 14
        position15encoder = bp.BrickPi.Encoder[self.port] - 20

        # now move to position 1 (we go until blocked, roughly)
        bp.BrickPi.MotorEnable[self.port] = 1
        try:
            bp.set_target_encoder(self.port, position15encoder - 120 * 14, 150)
        except:
            pass
        bp.BrickPiUpdateValues()
        position1encoder = bp.BrickPi.Encoder[self.port] + 80
        bp.BrickPi.MotorEnable[self.port] = 0

        # now, calculate stud distance
        stud_distance = abs(position1encoder - position15encoder) / 13

        self.current_position = 1

        # calculate all positions using Encoder value
        self.positions = []
        for x in range(15):
            if x == 0:
                self.positions.append(-1)
                continue
            thisposition = position1encoder + stud_distance * (x - 1)
            self.positions.append(thisposition)


    def set_position(self, position):
        bp.BrickPi.MotorEnable[self.port] = 1
        bp.BrickPiUpdateValues()
        bp.set_target_encoder(self.port, self.positions[position], 150)
        bp.BrickPi.MotorEnable[self.port] = 0
        bp.BrickPiUpdateValues()
        self.current_position = position
        bp.debug_out("encoder: " + str(bp.BrickPi.Encoder[self.port]))

    def reset(self):
        # move to regular position, that is, position 15
        self.set_position(14)
        # also move an extra stud, since we want to be sure to reset
        bp.BrickPiUpdateValues()
        bp.BrickPi.MotorEnable[self.port] = 1
        try:
            bp.set_target_encoder(self.port, bp.BrickPi.Encoder[self.port] - 100, 150)
        except:
            pass
        bp.BrickPi.MotorEnable[self.port] = 0





# The rotation class, which keeps the structure from not always rotating in the same direction
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


# Height class, which lowers the object stud by stud
class Height:
    def __init__(self, port):
        self.port = port
        bp.BrickPiUpdateValues()
        self.height1 = bp.BrickPi.Encoder[self.port]
        # assume position is something
        # 500 equals 90 degrees
        self.height2 = self.height1 - 500

    def lower(self):
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

    def reset(self):
        bp.BrickPi.MotorEnable[self.port] = 1
        bp.set_target_encoder(self.port, self.height1, 150)
        bp.BrickPi.MotorEnable[self.port] = 0

    

import sys
# Abort the scanning procedure, and return to regular position
def abort(xmovement, rotation, height):
    # we assume that the ymovement already is in regular position
    xmovement.reset()
    rotation.set_position(0)
    for i in range(20):
        height.lower()
    height.reset()
    sys.exit()


def check_if_abort(xmovement, rotation, height):
    bp.BrickPi.SensorType[setup.start_button_port] = bp.TYPE_SENSOR_TOUCH
    bp.BrickPiSetupSensors()
    bp.BrickPiUpdateValues()
    if bp.BrickPi.Sensor[setup.start_button_port]:
        abort(xmovement, rotation, height)
