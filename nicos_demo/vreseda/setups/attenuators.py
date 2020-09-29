#  -*- coding: utf-8 -*-

description = 'Attenuators'
group = 'optional'
display_order = 2

devices = dict(
    att0 = device('nicos.devices.generic.ManualSwitch',
        description = 'Attenuator 0: factor 3',
        states = ['in', 'out'],
        unit = '',
        maxage = 119,
        pollinterval = 60,
    ),
    att1 = device('nicos.devices.generic.ManualSwitch',
        description = 'Attenuator 1: factor 15',
        states = ['in', 'out'],
        unit = '',
        maxage = 119,
        pollinterval = 60,
    ),
    att2 = device('nicos.devices.generic.ManualSwitch',
        description = 'Attenuator 2: factor 30',
        states = ['in', 'out'],
        unit = '',
        maxage = 119,
        pollinterval = 60,
    ),
)
