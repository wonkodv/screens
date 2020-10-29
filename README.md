Configure Screens according to provided Setups, or the first setup that matches
all the connected devices or a default.  Default will enable all connected
devices and place them in a row in the order that xrandr reports them.

Other configurations are put in the SETUPS dict, which maps a  name to a list of
lists with device names plus xrandr options for that device.
