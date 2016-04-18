description = 'Some virtual vacuum devices for test purposes'

group = 'lowlevel'

devices = dict(
    vacuum = device('devices.generic.virtual.VirtualMotor',
                    description = 'Pressure in beam guide chamber',
                    abslimits = (0.001, 1000),
                    fmtstr = '%.3f',
                    unit = 'mbar',
                    jitter = 0.001,
                   ),
)
