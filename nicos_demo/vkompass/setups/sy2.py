description = 'Additional sample table devices'

group = 'optional'

devices = dict(
    sy2 = device('nicos.devices.generic.Axis',
        description = 'Additional sample table Y translation',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-30, 30),
            unit = 'mm',
        ),
        fmtstr = '%.1f',
        precision = 0.01,
    ),
)
