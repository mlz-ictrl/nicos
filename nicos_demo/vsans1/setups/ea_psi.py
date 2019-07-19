#  -*- coding: utf-8 -*-

description = 'Multipurpose EA power supply'
group = 'optional'

devices = dict(
    ea_psi_curr = device('nicos.devices.generic.VirtualMotor',
        description = 'Current regulated ea powersupply',
        fmtstr = '%.4f',
        abslimits = (0, 10),
        unit = 'A',
    ),
)
