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


    global xmovement, ymovement, height, rotation

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

    # let w be the width
    w = 12

    # iterate over each layer
    # we don't simply sweep with the probe over each layer, because that would be too costly
    # instead, we save the leftmost and rightmost non-zero positions, and start checking them
    # the performance improvement is all about this realization: if a row is enclosed with zero-rows, it has to be a zero-row itself
    # therefore, for each direction, save the leftmost and rightmost non-zero positions
    # we start at 1 and w-2
    nonzeros = [(1, w-2), (1, w-2), (1, w-2), (1, w-2)]
    for z in range(19):


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
                bp.set_target_encoder(setup.slide_probe_port, bp.BrickPi.Encoder[setup.slide_probe_port] - 40, 150)
                ymovement.calibrate()
                bp.BrickPi.MotorEnable[setup.slide_probe_port] = 0

                # the slide probe assumes regular position, minus 60
                xmovement = XMovement(setup.slide_probe_port)

                # now, go to the leftmost nonzero, and continue leftwards until a zero is found
                curpos = nonzeros[direction][0]
                newleftmost = w
                newrightmost = 0
                # we only go to position 1
                while curpos >= 1:
                    xmovement.set_position(curpos)
                    endpos = ymovement.find_first_block()
                    # halfreset ymovement
                    ymovement.halfreset()
                    if endpos == -1:
                        # now stop
                        for y in range(w):
                            layer[curpos][y] = 0
                        # also zero all other rows to the left
                        for x in range(curpos):
                            for y in range(w):
                                layer[x][y] = 0
                        break
                    else:
                        # set all before to 0, and the endpos to 1
                        if endpos > 0:
                            for y in range(endpos):
                                layer[curpos][y] = 0
                        layer[curpos][endpos] = 1
                        # also update newleftmost
                        newleftmost = min(newleftmost, curpos)
                        newrightmost = max(newrightmost, curpos)
                    curpos -= 1

                
                # now, scan from old leftmost + 1 until first zero after rightmost
                curpos = nonzeros[direction][0] + 1
                while curpos < w-1:
                    xmovement.set_position(curpos)
                    endpos = ymovement.find_first_block()
                    ymovement.halfreset()
                    if endpos == -1:
                        for y in range(w):
                            layer[curpos][y] = 0
                        if curpos >= nonzeros[direction][1]:
                            # now stop
                            # zero all other rows to right
                            for x in range(curpos+1,w):
                                for y in range(w):
                                    layer[x][y] = 0
                            break
                    else:
                        # set all before to 0, and the endpos to 1
                        if endpos > 0:
                            for y in range(endpos):
                                layer[curpos][y] = 0
                        layer[curpos][endpos] = 1
                        # also update newleftmost
                        newleftmost = min(newleftmost, curpos)
                        newrightmost = max(newrightmost, curpos)
                    curpos += 1
                            
                # now update the nonzeros
                nonzeros[direction] = (newleftmost, newrightmost)

                # full reset the ymvoement
                ymovement.reset()

                # reset the xmovement; i.e. move the slide probe to regular position
                xmovement.reset()

                # remember to rotate the base after scanning a direction
                rotation.next_position()
                
                # also rotate the layer grid 90 degrees in the same direction as the physical rotation (hmm, is that important? i suspect not)
                layer = rotate_layer(layer)
                
                """
                # printe the (rotated) layer
                for row in layer:
                    for s in row:
                        print(str(s) + " ", end="")
                    print(" ")
                """

            # fix corners
            # if the corners have a zero as neighbor, then it is a zero; otherwise, it is a one
            if layer[0][1] == 0 or layer[1][0] == 0:
                layer[0][0] = 0
            else:
                layer[0][0] = 1
            if layer[0][w-2] == 0 or layer[1][w-1] == 0:
                layer[0][w-1] = 0
            else:
                layer[0][w-1] = 1
            if layer[w-2][0] == 0 or layer[w-1][1] == 0:
                layer[w-1][0] = 0
            else:
                layer[w-1][0] = 1
            if layer[w-2][w-1] == 0 or layer[w-1][w-2] == 0:
                layer[w-1][w-1] = 0
            else:
                layer[w-1][w-1] = 1


            # check if layer is empty. if that is so, don't scan the rest of the layers
            is_empty = True
            for x in range(w):
                for y in range(w):
                    if layer[x][y] != 0:
                        is_empty = False
            if is_empty:
                stop_scanning = True

        # rotate the layer once so that it is prepared for printing
        layer = rotate_layer(layer)

        # append the layer to the matrix3d
        matrix3d.append(layer)

        # now lower the object
        height.lower()


    # return the presence matrix
    return matrix3d



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
        stud_distance = 1450
        stop_position = self.move_till_stop(foolhardy=True)
        self.positions = []
        for y in range(-7, 11):
            self.positions.append(stop_position + (y + 7) * stud_distance)
        # then reset
        self.reset()

    def set_position(self, position):
        bp.BrickPi.MotorEnable[self.motor_port] = 1
        bp.set_target_encoder(self.motor_port, self.positions[position], 200)
        bp.BrickPi.MotorEnable[self.motor_port] = 0


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
            color_val = bp.BrickPi.Sensor[self.sensor_port]
            if color_val > 105:
                break
            if not foolhardy:
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
        for i in range(5):
            try:
                bp.set_target_encoder(self.motor_port, self.positions[5], 200)
                break
            except:
                print("strange exception")
                time.sleep(5)
        bp.BrickPi.MotorEnable[self.motor_port] = 0

    def reset(self):
        # move probe to regular position
        bp.BrickPi.MotorEnable[self.motor_port] = 1
        for i in range(5):
            try:
                bp.set_target_encoder(self.motor_port, self.regular_position, 200)
                break
            except:
                print("strange exception")
                time.sleep(5)
        bp.BrickPi.MotorEnable[self.motor_port] = 0





# The XMovement class, which slides the probe stud by stud in the x direction
class XMovement:

    def __init__(self, port):
        self.port = port
        bp.BrickPiUpdateValues()

        # we assume regular position, so it starts at stud 14, plus circa 60 units
        self.current_position = 14
        position15encoder = bp.BrickPi.Encoder[self.port]

        # now move to position 1 (we go until blocked, roughly)
        bp.BrickPi.MotorEnable[self.port] = 1
        try:
            bp.set_target_encoder(self.port, position15encoder - 120 * 14, 150)
        except:
            pass
        bp.BrickPiUpdateValues()
        position1encoder = bp.BrickPi.Encoder[self.port] + 150
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
        for i in range(5):
            try:
                bp.set_target_encoder(self.port, self.positions[position], 150)
                break
            except:
                print("strange exception")
                time.sleep(5)
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
            bp.set_target_encoder(self.port, bp.BrickPi.Encoder[self.port] + 100, 150)
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
            # Add slightly more, due to some degrees of freedom that alter these values
            position = bp.BrickPi.Encoder[self.port] + i*14*720
            if i > 0:
                position += 450
            self.positions.append(position)
        self.current_position = 0
        self.set_position(1)
        time.sleep(2)
        self.set_position(0)

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

    def reset(self):
        self.set_position(0)


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



def assume_printer_position():
    global xmovement, ymovement, height
    if "height" in globals():
        height.lower()
        height.lower()
        height.reset()
    if "xmovement" not in globals():
        xmovement = XMovement(setup.slide_probe_port)
    xmovement.set_position(5)
    if "ymovement" not in globals():
        ymovement = YMovement(setup.eject_probe_port, setup.probe_sensor_port)
        bp.BrickPi.MotorEnable[setup.eject_probe_port] = 1
        bp.set_target_encoder(setup.eject_probe_port, bp.BrickPi.Encoder[setup.eject_probe_port] + 17000, 200)
        bp.BrickPi.MotorEnable[setup.eject_probe_port] = 0
    else:
        ymovement.set_position(7)

    

    

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

def reset():
    global xmovement, ymovement, height, rotation
    if "ymovement" in globals():
        ymovement.reset()
    if "xmovement" in globals():
        xmovement.reset()
    if "rotation" in globals():
        rotation.reset()
    if "height" in globals():
        height.reset()



def check_if_abort(xmovement, rotation, height):
    bp.BrickPi.SensorType[setup.start_button_port] = bp.TYPE_SENSOR_TOUCH
    bp.BrickPiSetupSensors()
    bp.BrickPiUpdateValues()
    if bp.BrickPi.Sensor[setup.start_button_port]:
        abort(xmovement, rotation, height)
