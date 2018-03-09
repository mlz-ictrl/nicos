description = 'Various virtual/logical motors in AMOR'

includes = ['analyser', 'counter', 'diaphragm', 'distances', 'sample']

devices = dict(
    controller_lm = device('nicos_sinq.amor.devices.logical_motor.AmorLogicalMotorHandler',
        description = 'Logical motors controller',
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
        sample = 'dsample',
        polarizer = 'dpolarizer',
        slit1 = 'dslit1',
        slit2 = 'dslit2',
        slit3 = 'dslit3',
        slit4 = 'dslit4',
        analyzer = 'danalyzer',
        detector = 'ddetector',
        lowlevel = True
    ),
    m2t = device('nicos_sinq.amor.devices.logical_motor.AmorLogicalMotor',
        description = 'Logical motor monochromator two theta',
        motortype = 'm2t',
        controller = 'controller_lm'
    ),
    s2t = device('nicos_sinq.amor.devices.logical_motor.AmorLogicalMotor',
        description = 'Logical motor sample two theta',
        motortype = 's2t',
        controller = 'controller_lm'
    ),
    ath = device('nicos_sinq.amor.devices.logical_motor.AmorLogicalMotor',
        description = 'Logical Motor analyser theta',
        motortype = 'ath',
        controller = 'controller_lm'
    ),
)
