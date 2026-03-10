description = 'Slits before detector'

group = 'optional'

devices = dict(
    dslit = device('nicos.devices.generic.Axis',
        description = 'Slit before detector',
        motor = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-5.5, 30),
        ),
        precision = 0.05,
        offset = 0,
        maxtries = 10,
    ),
)
