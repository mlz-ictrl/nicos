# -*- coding: utf-8 -*-

description = 'Virtual polarizer motor setup'
group = 'lowlevel'
display_order = 25

devices = dict(
    polarizer = device('nicos_mlz.kws1.devices.polarizer.Polarizer',
        description = 'high-level polarizer switcher',
        switcher = 'pol_switch',
        switchervalues = ('out', 'in'),
        flipper = 'flipper',
    ),
    pol_switch = device('nicos_mlz.kws1.devices.virtual.StandinSwitch',
        description = 'switch polarizer or neutron guide',
        states = ['out', 'in'],
    ),
    flipper = device('nicos_mlz.kws1.devices.virtual.StandinSwitch',
        description = 'spin flipper after polarizer',
        states = ['off', 'on'],
    ),
)
