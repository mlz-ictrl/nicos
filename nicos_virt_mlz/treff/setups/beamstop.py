description = 'Beamstop device'

group = 'optional'

devices = dict(
    beamstop = device('nicos.devices.generic.Axis',
        description = 'Beamstop position',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-44.8586, 0.1),
            unit = 'mm',
            speed = 1,
        ),
        precision = 0.01,
        fmtstr = '%.3f',
    ),
)
