description = 'Sample slits'

group = 'lowlevel'

devices = dict(
    ssy = device('nicos.devices.generic.Axis',
        description = 'Y position of center of sample slit',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-25, 25),
            unit = 'mm',
        ),
        precision = 0.01,
    ),
    ssz = device('nicos.devices.generic.Axis',
        description = 'Z position of center of sample slit',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-25, 25),
            unit = 'mm',
        ),
        precision = 0.01,
    ),
)
