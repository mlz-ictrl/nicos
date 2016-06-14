# -*- coding: utf-8 -*-

description = "Virtual beam shutter setup"
group = "lowlevel"
display_order = 5

devices = dict(
    shutter    = device('devices.generic.ManualSwitch',
                        description = 'virtual shutter',
                        states = ['open', 'closed'],
                       ),
)
