description = 'CAEN ELS FAST powersupplies'

group = 'optional'

devices = dict(
    caenels1 = device('nicos.devices.generic.VirtualMotor',
        description = 'FAST power supply 1',
        abslimits = (-1, 1),
        fmtstr = '%.4f',
        precision = 0.0001,
        unit = 'A',
    ),
    caenels2 = device('nicos.devices.generic.VirtualMotor',
        description = 'FAST power supply 2',
        abslimits = (-1, 1),
        fmtstr = '%.4f',
        precision = 0.0001,
        unit = 'A',
    ),
)
