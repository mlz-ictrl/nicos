#  -*- coding: utf-8 -*-

description = 'setup for the small chopper'
group = 'optional'
display_order = 65

tango_base = 'tango://phys.kws2.frm2:10000/kws2/'

devices = dict(
    smallchopper_on = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'switch the small chopper on or off',
        tangodevice = tango_base + 'sps/smallchopper_enable',
        mapping = {'on': 3, 'off': 0},
    ),
    # TODO: record speeds pre-set to Maxon controller
    smallchopper_speed = device('nicos.devices.tango.NamedDigitalOutput',
        description = 'switch the small chopper between two preset speeds',
        tangodevice = tango_base + 'sps/smallchopper_speed',
        mapping = {'slow': 1, 'fast': 0},
    ),
)

extended = dict(
)
