# -*- coding: utf-8 -*-

description = "Virtual beam shutter setup"
group = "lowlevel"
display_order = 5

devices = dict(
    shutter    = device('devices.generic.ManualSwitch',
                        description = 'virtual shutter',
                        states = ['open', 'closed'],
                       ),
    nl3a_shutter = device('devices.generic.ManualSwitch',
                        description = 'NL3a shutter status',
                        states = ['open', 'closed'],
                       ),
    sixfold_shutter = device('devices.generic.ManualSwitch',
                        description = 'Sixfold shutter status',
                        states = ['open', 'closed'],
                       ),
)
