description = 'sample table goniometer setup'

group = 'optional'

excludes = ['sampletable']

devices = dict(
    x = device('nicos.devices.generic.Axis',
        description = 'sample table x translation',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-75, 75),
            unit = 'mm',
            speed = 1,
        ),
        precision = 0.01,
        fmtstr = '%.2f',
    ),
    y = device('nicos.devices.generic.Axis',
        description = 'sample table y translation',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-75, 75),
            unit = 'mm',
            speed = 1,
        ),
        precision = 0.01,
        fmtstr = '%.2f',
    ),
    z = device('nicos.devices.generic.Axis',
        description = 'sample table z translation',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (0, 25),
            unit = 'mm',
            speed = 1,
        ),
        precision = 0.01,
        fmtstr = '%.2f',
    ),
    phi = device('nicos.devices.generic.Axis',
        description = 'sample table phi rotation',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (0, 360),
            unit = 'deg',
            speed = 1,
        ),
        precision = 0.01,
        fmtstr = '%.2f',
    ),
    chi = device('nicos.devices.generic.Axis',
        description = 'sample table chi rotation',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (0, 160),
            unit = 'deg',
            speed = 1,
        ),
        precision = 0.01,
        fmtstr = '%.2f',
    ),
)
