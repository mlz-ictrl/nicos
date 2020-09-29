#  -*- coding: utf-8 -*-

description = 'Arm 0 B'

group = 'lowlevel'

includes = ['cbox_0b']

devices = dict(
    T_arm0b_coil1 = device('nicos.devices.generic.VirtualTemperature',
        description = 'Arm 0 (B) coil 1 temperature',
        abslimits = (0, 60),
        curvalue = 23,
        fmtstr = '%.1f',
        unit = 'degC',
        pollinterval = 10,
        maxage = 21,
    ),
    T_arm0b_coil2 = device('nicos.devices.generic.VirtualTemperature',
        description = 'Arm 0 (B) coil 2 temperature',
        abslimits = (0, 60),
        curvalue = 23,
        fmtstr = '%.1f',
        unit = 'degC',
        pollinterval = 10,
        maxage = 21,
    ),
)
