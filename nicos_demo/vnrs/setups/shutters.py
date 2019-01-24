# -*- coding: utf-8 -*-
description = 'Shutter devices'

group = 'lowlevel'

devices = dict(
    shutter1 = device('nicos.devices.generic.Switcher',
        description = 'Shutter 1',
        moveable = device('nicos.devices.generic.ManualSwitch',
            states = [0, 1],
        ),
        mapping = dict(open = 1, closed = 0),
        fallback = '<undefined>',
        precision = 0,
    ),
    shutter2 = device('nicos.devices.generic.Switcher',
        description = 'Shutter 2',
        moveable = device('nicos.devices.generic.ManualSwitch',
            states = [0, 1],
        ),
        mapping = dict(open = 1, closed = 0),
        fallback = '<undefined>',
        precision = 0,
    ),
    fastshutter = device('nicos.devices.generic.Switcher',
        description = 'Fast shutter',
        moveable = device('nicos.devices.generic.ManualSwitch',
            states = [0, 1],
        ),
        mapping = dict(open = 1, closed = 0),
        fallback = '<undefined>',
        precision = 0,
    ),
)
