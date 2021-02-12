#  -*- coding: utf-8 -*-

description = 'Setup for the Saphire Filter in primary beam'

includes = ['monoturm']
group = 'optional'

devices = dict(
    saph_mot = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        abslimits = (-133.4, 120),
        speed = 10,
        lowlevel = True,
        curvalue = -8,
    ),
    saph = device('nicos.devices.generic.Switcher',
        description = 'saphire filter',
        moveable = 'saph_mot',
        mapping = {'in': -133,
                   'out': -8},
        blockingmove = True,
        precision = 1,
    ),
)
