#!/bin/python

"""
Configure Screens according to provided Setups, or the first setup that matches
all the connected devices or a default.  Default will enable all connected
devices and place them in a row in the order that xrandr reports them.

Other configurations are put in the SETUPS dict, which maps a  name to a list of
lists with device names plus xrandr options for that device.
"""

import subprocess
import re
import functools
import time

SETUPS = {
    'work': [
            ['DisplayPort-3', '--primary'],
            ['DisplayPort-2', '--right-of', 'DisplayPort-3'],
            ['eDP', '--below', 'DisplayPort-3'],
    ]
}


def get_setup_names():
    return list(SETUPS)


def call(args):
    p = subprocess.Popen(['xrandr', *args],
                         stdout=subprocess.PIPE,
                         stdin=subprocess.DEVNULL,
                         universal_newlines=True,
                         )
    if not p.wait() == 0:
        raise IOError(args, p.returncode, p.stdout.read(), p.stderr.read())
    return p.stdout.read()


_devices_cache = (0, None)


def devices():
    """ Get Dict of all devices to whether they are connected.

    Results are cached for 1 Second because multiple calls would just take up
    time, but the result could change after a while.
    """

    global _devices_cache
    t, devs = _devices_cache
    t2 = time.time()
    if t2 - t > 1:
        text = call(())
        devs = {
            dev: not dis for (dev, dis) in re.findall(
                r"^([^\s]*)\s+(dis)?connected",
                text,
                re.M
            )
        }
        _devices_cache = (t2, devs)
    return devs


def find_setup():
    for s in SETUPS.values():
        if test_setup(s):
            return s
    return None


def test_setup(s):
    enabled_devs = set(d for (d, e) in devices().items() if e)
    setup_devs = set(d for (d, *o) in s)
    return setup_devs == enabled_devs


def default_setup():
    prev = None
    setup = []
    for dev, connected in devices().items():
        if connected:
            if prev is None:
                setup.append([dev, '--primary'])
            else:
                setup.append([dev, '--right-of', prev])
            prev = dev
    return setup


def get_setup(setup):
    if setup is None:
        s = find_setup()
        if not s:
            s = default_setup()
    else:
        s = SETUPS[setup]
    return s


def setup_to_args(s):
    args = []
    off_devs = set(devices())
    for (device, *options) in s:
        args += "--output", device, '--preferred',
        args += options
        off_devs.remove(device)
    for d in off_devs:
        args += '--output', d, '--off'
    return args


def main(setup=None):
    s = get_setup(setup)
    a = setup_to_args(s)
    call(a)
    return 0
