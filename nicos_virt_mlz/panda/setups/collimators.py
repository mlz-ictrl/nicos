#  -*- coding: utf-8 -*-

description = 'Setup for the CA1 lift in primary beam and CA2 adjustment motor'

includes = ['monoturm', 'sampletable']
group = 'optional'

devices = dict(
    ca1_mot = device('nicos.devices.generic.VirtualMotor',
        description = 'Stepper motor to move the collimator lift',
        unit = 'mm',
        abslimits = (-1, 760),
        speed = 1,
    ),
    ca1 = device('nicos.devices.generic.Switcher',
        description = 'Collimator CA1 lift',
        moveable = 'ca1_mot',
        mapping = {'none': 0, '20m': 310, '60m': 540, '40m': 755},
        blockingmove = True,
        precision = 1,
    ),
)
