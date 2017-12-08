description = 'Slit ZB0'

group = 'optional'

devices = dict(
    # zb0 is at exit of NOK5a (so on its sample side)
    zb0_m = device('nicos.devices.generic.Axis',
        description = 'zb0 axis',
        motor = device('nicos.devices.generic.virtual.VirtualMotor',
            abslimits = (-184, -0.1),
            userlimits = (-155.7889, -0.1),
            unit = 'mm',
            speed = 5.,
        ),
        precision = 0.05,
    ),
    zb0 = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        description = 'zb0, singleslit',
        motor = 'zb0_m',
        nok_start = 4121.5,
        nok_length = 13,
        nok_end = 4134.5,
        nok_gap = 1,
        masks = {
            'slit': 0,
            'point': 0,
            'gisans': -100,
        },
        unit = 'mm',
    ),
)
