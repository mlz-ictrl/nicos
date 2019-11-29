# -*- coding: utf-8 -*-

description = 'Virtual polarizer setup'
group = 'lowlevel'
display_order = 60

devices = dict(
    polarizer = device('nicos_mlz.kws1.devices.virtual.StandinSwitch',
        description = 'high-level polarizer switcher',
        states = ['out', 'up', 'down'],
    ),
)

extended = dict(
    representative = 'polarizer',
)
