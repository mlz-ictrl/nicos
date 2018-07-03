# -*- coding: utf-8 -*-
description = 'ANTARES shutter devices'

group = 'lowlevel'

devices = dict(
    shutter1 = device('nicos.devices.generic.ManualSwitch',
        description = 'Shutter 1',
        states = ['open', 'closed'],
    ),
    shutter2 = device('nicos.devices.generic.ManualSwitch',
        description = 'Shutter 2',
        states = ['open', 'closed'],
    ),
    fastshutter = device('nicos.devices.generic.ManualSwitch',
        description = 'Fast shutter',
        states = ['open', 'closed'],
    ),
)
