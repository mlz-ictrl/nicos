#  -*- coding: utf-8 -*-

description = 'Setup of a Monochromator Focusing Box on PANDA'

group = 'lowlevel'

extended = dict(dynamic_loaded = True)

devices = dict(
    focibox = device('nicos_virt_mlz.panda.devices.stubs.Focibox',
        description = 'reads monocodes and returns which mono is connected',
        unit = '',
    ),
    mfh = device('nicos.devices.generic.DeviceAlias',
        alias = '',
    ),
    mfv = device('nicos.devices.generic.DeviceAlias',
        alias = '',
    ),
)
