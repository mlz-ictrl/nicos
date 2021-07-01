#  -*- coding: utf-8 -*-

description = 'Arm 0 A'

group = 'lowlevel'

includes = ['cbox_0a']

devices = dict(
    T_arm0a_coil1 = device('nicos.devices.generic.VirtualTemperature',
        description = 'Arm 0 (A) coil 1 temperature',
        abslimits = (0, 50),
        curvalue = 22,
        fmtstr = '%.1f',
        unit = u'degC',
        pollinterval = 10,
        maxage = 21,

    ),
    T_arm0a_coil2 = device('nicos.devices.generic.VirtualTemperature',
        description = 'Arm 0 (A) coil 2 temperature',
        abslimits = (0, 50),
        curvalue = 22,
        fmtstr = '%.1f',
        unit = u'degC',
        pollinterval = 10,
        maxage = 21,
    ),
)
