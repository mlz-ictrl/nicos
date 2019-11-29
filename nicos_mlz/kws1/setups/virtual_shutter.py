# -*- coding: utf-8 -*-

description = 'Virtual beam shutter setup'
group = 'lowlevel'
display_order = 5

devices = dict(
    shutter = device('nicos_mlz.kws1.devices.virtual.StandinSwitch',
        description = 'shutter control',
        states = ['open', 'closed'],
    ),
    nl3b_shutter = device('nicos_mlz.kws1.devices.virtual.StandinSwitch',
        description = 'NL3b shutter status',
        states = ['open', 'closed'],
    ),
    sixfold_shutter = device('nicos_mlz.kws1.devices.virtual.StandinSwitch',
        description = 'Sixfold shutter status',
        states = ['open', 'closed'],
    ),
)

extended = dict(
    representative = 'shutter',
)
