# lego3dcopier
The code for a Lego Mindstorms robot that scans a Lego construction and proceeds to build an identical copy of it.


# Setup

Install BrickPi.

Install nxt-python using `python3 nxt-python/setup.py install`.

Install PyUSB using `pip3 install pyusb`.

Enable USB: Run `groupadd lego` followed by `usermod -a -G lego <username>`. Then create a file at /etc/udev/rules-d/70-lego.rules with the contents `SUBSYSTEM=="usb", ATTRS{idVendor}=="0694", GROUP="lego", MODE="0660"`.

After all this, reboot.

Then modify the `nxt-python.config` file. Symlink it to the real config file using `ln -s nxt-python.config ~/.nxt-python`.
