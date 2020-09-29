# -*- coding: utf-8 -*-

description = 'collimator'

group = 'optional'

devices = dict(
    coll_rot = device('nicos.devices.generic.VirtualMotor',
        description = 'Rotation of collimator',
        unit = 'deg',
        abslimits = (-10, 10),
    ),
    coll_ang = device('nicos.devices.generic.VirtualMotor',
        description = 'Tilt of collimator',
        unit = 'deg',
        abslimits = (-10, 10),
    ),
)
