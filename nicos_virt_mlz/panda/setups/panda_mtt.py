# -*- coding: utf-8 -*-

description = 'setup for Beckhoff PLC mtt devices on PANDA'

group = 'lowlevel'

devices = dict(
    mtt = device('nicos.devices.generic.Axis',
        description = 'Virtual MTT axis that exchanges block automatically '
                      '(must be used in "automatic" mode).',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-122, -25),
            unit = 'deg',
            speed = 1,
            curvalue = -40,
        ),
        precision = 0.001,
    ),
)
