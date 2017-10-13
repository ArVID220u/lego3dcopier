# lego3dcopier
The code for a Lego Mindstorms robot that scans a Lego construction and proceeds to build an identical copy of it.


## Setup

Install BrickPi.

Install nxt-python using `./nxt-python/install.sh`.

Install PyUSB using `pip3 install pyusb`.

Enable USB: Run `groupadd lego` followed by `usermod -a -G lego <username>`. Then create a file at /etc/udev/rules-d/70-lego.rules with the contents `SUBSYSTEM=="usb", ATTRS{idVendor}=="0694", GROUP="lego", MODE="0660"`.

After all this, reboot.

Then modify the `nxt-python.config` file. Symlink it to the real config file using `ln -s ~/lego3dcopier/nxt-python.config ~/.nxt-python`.

## Legotile Algorithm

The scanner produces the following data for each stud position: whether a brick is present, not present, or if that is impossible to determine. This yields what I call a presence matrix, i.e. a 3D matrix consisting of 1s where a brick is present, 0s where no brick is present, and -1s where we can't determine that.

This presence matrix needs to be converted into explicit build instructions of the type "move brick T to position (X, Y, Z)". The build instructions need to be created in such a way that the resulting structure is as connected and as rigid as possible. This conversion process is not trivial, which is why I call it the Legotile Algorithm.

The Legotile Algorithm receives as input the presence matrix. First, it converts the -1s of the presence matrix into 0s or 1s by following some heuristic rules. The most significant such rule is based on the obsevation that no 1 can be surrounded by two 0s on either side of it, since the only available bricks are 4x2, 2x4 and 2x2.

After having converted the presence matrix into a definite presence matric consisting of only 1s and 0s, the Legotile Algorithm proceeds to place bricks, layer by layer. Since the layers are fairly small (12x12), we can basically try all possible placements of lego bricks for every layer, and determine the best one based on a heuristic penalty-awarding system. Due to pruning and restrictions in the search space the time complexity is difficult to analyze, however, it should be clear that we cannot just try all possible placements naïvely, since that would run in exponential time (to the number of studs in a layer).

Rather, the Legotile Algorithm adopts the central idea of Dijkstra's algorithm. We want to minimize our penalty when we go from our original layer of 1s and 0s, to a layer where the 1s are completely covered by bricks and the 0s are not. We can, for the sake of our Dijkstra analogy, view our problem as a shortest path problem, where we want to go from A to B while minimizing the distance (here, penalty). This is the main idea of the Legotile Algorithm.

The penalty for a layer takes into account two things. First, the penalty increases with the number of 2x2-bricks present in the layer, since 2x2-bricks are generally not as good as the larger bricks in terms of rigidity. Second, the penalty increases with the number of shared vertical boundaries of bricks between two adjacent layers. That is, if a vertical boundary between two bricks is in the same place in two adjacent layers, the penalty will increase.

Finally, the Legotile Algorithm also checks to make sure that the structure is connected, i.e. that all bricks are connected to each other in some way. This is done by using the union-find data structure – the stud positions of each individual brick of each layer are combined ("unioned"), and then the number of disjoint sets are counted (and that number should be as low as possible).

The Legotile Algorithm returns a 3D matrix, where every cell indicate the index of the lego brick that covers it. 0 still signifies that a position is free.

