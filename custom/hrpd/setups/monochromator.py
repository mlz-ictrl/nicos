description = 'Monochromator devices'

group = 'lowlevel'

devices = dict(
    crystal_m = device('devices.generic.Axis',
        description = 'Monochromator changer rotation table',
        motor = device('devices.generic.VirtualMotor',
            abslimits = (-1, 181),
            unit = 'deg',
        ),
        precision = 0.01,
    ),
    crystal = device('devices.generic.Switcher',
        description = 'Monochromator changer',
        moveable = 'crystal_m',
        mapping = {
            'Si': 0.,
            'Ge': 180.,
        },
        precision = 0.01,
        unit = '',
    ),
)
