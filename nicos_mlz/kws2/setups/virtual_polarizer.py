# -*- coding: utf-8 -*-

description = 'Virtual polarizer setup'
group = 'lowlevel'
display_order = 60

devices = dict(
    polarizer = device('nicos.devices.generic.ManualSwitch',
        description = 'high-level polarizer switcher',
        states = ['out', 'up', 'down'],
    ),
)
