# -*- coding: utf-8 -*-

description = 'lens switching devices'
group = 'lowlevel'
display_order = 75

devices = dict(
    lenses = device('nicos_mlz.kws1.devices.lens.Lenses',
        description = 'high-level lenses device',
        io = 'lens_io',
    ),
    lens_io = device('nicos.devices.generic.VirtualMotor',
        description = 'lens I/O device',
        unit = '',
        abslimits = (0, 7),
        lowlevel = True,
    ),
)

extended = dict(
    representative = 'lenses',
)
