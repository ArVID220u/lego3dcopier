#!/usr/bin/env python3

import scanner
import printer
import setup

import subprocess
import os


# The main function, which should initiate the check for a button press, and then start the copying process
def main():
    # check for button press
    button_press = True
    if button_press:
        try:
            copy()
        finally:
            # We always want to keep regular position
            reset()



# Reset everything into regular position
def reset():
    scanner.reset()
    printer.reset()


# The copying procedure
def copy():
    # WE ASSUME REGULAR POSITION
    # start by scanning, which generates a presence matrix

    # now, we want to run the legotile algorithm
    # the legotile algorithm is a cpp program and thus needs to be communicated with using stdin/stdout

    # create a temporary in file which can be sent to the algorithm
    scanneroutput = "scanneroutput.in"

    if setup.debug:
        otherinput = input()
        if otherinput.endswith(".in"):
            scanneroutput = otherinput
    if scanneroutput == "scanneroutput.in":

        presence_matrix = scanner.scan()

        with open(scanneroutput, "w") as scanneroutputfile:
            # write the presence matrix to it
            # first, we write the dimensions
            scanneroutputfile.write(str(presence_matrix[0].size()) + " " + str(presence_matrix.size()) + "\n")
            # then, we write out the complete matrix
            for layer in presence_matrix:
                for row in layer:
                    for item in row:
                        scanneroutputfile.write(str(item) + " ")
                    scanneroutputfile.write("\n")
                scanneroutputfile.write("\n")
            # finished!


    # now send this data to the legotile algorithm and run it
    legotile_output = ""
    with open(scanneroutput, "rb") as scanneroutputfile:
        legotile_output = subprocess.check_output([os.path.abspath(setup.legotile_algorithm_executable)], stdin=scanneroutputfile).decode("utf-8")


    # now build these build_instructions
    printer.build(legotile_output)

    





if __name__ == "__main__":
    main()
