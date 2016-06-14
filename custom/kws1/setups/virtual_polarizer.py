# -*- coding: utf-8 -*-

description = "Virtual polarizer setup"
group = "lowlevel"
display_order = 60

devices = dict(
    polarizer   = device('kws1.polarizer.Polarizer',
                         description = "high-level polarizer switcher",
                         switcher = 'pol_switch',
                         flipper = 'flipper'
                        ),

    pol_switch  = device("devices.generic.ManualSwitch",
                         description = "switch polarizer or neutron guide",
                         states = ['pol', 'ng'],
                        ),

    flipper     = device("devices.generic.ManualSwitch",
                         description = "spin flipper after polarizer",
                         states = ['off', 'on'],
                        ),
)
