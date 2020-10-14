#  -*- coding: utf-8 -*-
description = 'Analyser rotation'

group = 'optional'

devices = dict(
    analysator_rot = device('nicos.devices.generic.VirtualMotor',
        description = 'Rotation analyer (motor)',
        fmtstr = '%.3f',
        unit = 'deg',
        speed = 5,
        abslimits = (-5.0, 60.0),
    ),
)
