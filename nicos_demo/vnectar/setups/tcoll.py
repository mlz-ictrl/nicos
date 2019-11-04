description = 'Thermal collimator'

group = 'optional'

tango_base = 'tango://phytron02.nectar.frm2.tum.de:10000/'

devices = dict(
    drum_m = device('nicos.devices.generic.VirtualMotor',
        abslimits = (-10, 370),
        unit = 'deg',
        speed = 7.5,
        lowlevel = True,
    ),
    drum = device('nicos.devices.generic.Axis',
        motor = 'drum_m',
        # coder = 'drum_c',  # coder not working for multiturns (Resolver)
        precision = 0.05,
        lowlevel = True,
    ),
    tcoll = device('nicos.devices.generic.Switcher',
        description = 'Thermal collimator',
        precision = 0.01,
        moveable = 'drum',
        mapping = {
            '1': 0,
            '2': 90,
            '3': 180,
            '4': 270,
        },
    ),
)
