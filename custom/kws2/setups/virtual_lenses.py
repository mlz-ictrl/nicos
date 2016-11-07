# -*- coding: utf-8 -*-

description = 'Virtual lens switching devices'
group = 'lowlevel'
display_order = 75

devices = dict(
    lenses    = device('kws1.lens.Lenses',
                       description = 'high-level lenses device',
                       io = 'lens_io',
                      ),

    lens_io   = device('devices.generic.VirtualMotor',
                       description = 'lens I/O device',
                       abslimits = (0, 7),
                       unit = '',
                       lowlevel = True,
                      ),
)
