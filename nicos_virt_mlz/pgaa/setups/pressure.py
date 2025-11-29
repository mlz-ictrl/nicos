description = 'Vacuum sensors of sample chamber'

group = 'lowlevel'

devices = dict(
    chamber_pressure = device('nicos.devices.generic.VirtualMotor',
        description = 'Chamber pressure',
        jitter = 0.2,
        abslimits = (0, 1000),
        unit = 'mbar',
        curvalue = 0.5,
    ),
)
