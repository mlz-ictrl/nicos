# -*- coding: utf-8 -*-
description = 'Axes in detector test table'

group = 'optional'

devices = dict(
    det_ax = device('nicos.devices.generic.VirtualMotor',
        description = 'X axis',
        abslimits = (-1000, 1000),
        unit = 'mm',
    ),
    det_ay = device('nicos.devices.generic.VirtualMotor',
        description = 'Y axis',
        abslimits = (-1000, 1000),
        unit = 'mm',
    ),
)
