description = 'Various virtual/logical motors in AMOR'

group='lowlevel'

devices = dict(
    controller_lm = device(
        'nicos_sinq.amor.devices.logical_motor.AmorLogicalMotorHandler',
        description = 'Logical motors controller',
        distances = 'Distances',
        soz = 'soz',
        com = 'com',
        cox = 'cox',
        coz = 'coz',
        d1b = 'd1b',
        d2b = 'd2b',
        d3b = 'd3b',
        d4b = 'd4b',
        aoz = 'aoz',
        aom = 'aom',
        d1t = 'd1t',
        d2t = 'd2t',
        d3t = 'd3t',
        d4t = 'd4t',
        lowlevel = True
    ),
)
