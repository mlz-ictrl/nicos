#  -*- coding: utf-8 -*-

description = 'Fast Shutter'

group = 'optional'

devices = dict(
    fastshutter = device('nicos.devices.generic.ManualSwitch',
        description = 'Fast shutter',
        states = ('open', 'closed'),
    ),
)
