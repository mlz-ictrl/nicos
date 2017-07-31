description = 'Monochromator devices'

group = 'lowlevel'

devices = dict(
    crystal_m = device('nicos.devices.generic.Axis',
        description = 'Monochromator changer rotation table',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-1, 181),
            unit = 'deg',
        ),
        precision = 0.01,
    ),
    crystal = device('nicos.devices.generic.Switcher',
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
