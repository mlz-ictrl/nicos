# -*- coding: utf-8 -*-

description = 'Shutter setup'
group = 'lowlevel'

devices = dict(
    expshutter = device('nicos.devices.generic.ManualSwitch',
        description = 'Experiment shutter',
        states = ['closed', 'open'],
    ),
)
