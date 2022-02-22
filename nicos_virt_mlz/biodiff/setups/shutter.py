# -*- coding: utf-8 -*-

description = 'Shutter setup'
group = 'lowlevel'

devices = dict(
    gammashutter = device('nicos.devices.generic.ManualSwitch',
        description = 'Gamma shutter (virtual)',
        states = ['open', 'closed'],
    ),
    photoshutter = device('nicos.devices.generic.ManualSwitch',
        description = 'Photo shutter (virtual)',
        states = ['open', 'closed'],
    ),
)
