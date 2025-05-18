description = 'motors that are available by default (simulated)'

group = 'optional'

excludes = ['motors']

devices = dict(
    sry_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample rotation y-Axis motor',
        fmtstr = '%.2f',
        abslimits = (-400, 400),
        speed = 10,
        requires = dict(level='guest'),
        unit = 'deg',
    ),
    sry = device('nicos.devices.generic.Axis',
        description = 'Sample rotation y-Axis',
        motor = 'sry_m',
        precision = 0.001,
    ),
)
