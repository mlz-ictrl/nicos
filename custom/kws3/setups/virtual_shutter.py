# -*- coding: utf-8 -*-

description = 'Virtual shutter setup'
group = 'lowlevel'
display_order = 5

devices = dict(
    shutter         = device('nicos.devices.generic.ManualSwitch',
                             description = 'shutter control',
                             states = ['open', 'closed'],
                            ),
    nl3a_shutter    = device('nicos.devices.generic.ManualSwitch',
                             description = 'Neutron guide 3a shutter status',
                             states = ['open', 'closed'],
                            ),
    sixfold_shutter = device('nicos.devices.generic.ManualSwitch',
                             description = 'Sixfold shutter status',
                             states = ['open', 'closed'],
                            ),
)
