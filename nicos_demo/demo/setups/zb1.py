description = 'Slit ZB1'

group = 'optional'

devices = dict(
    # zb1 is at exit of NOK5b (so on its sample side)
    zb1_m = device('nicos.devices.generic.Axis',
        description = 'zb1 axis',
        motor = device('nicos.devices.generic.virtual.VirtualMotor',
            abslimits = (-184, -0.1),
            userlimits = (-146.0656, -0.1),
            unit = 'mm',
            speed = 5.,
        ),
        precision = 0.05,
    ),
    zb1 = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        description = 'zb1, singleslit',
        motor = 'zb1_m',
        nok_start = 5856.5,
        nok_length = 13,
        nok_end = 5862.5,
        nok_gap = 1,
        masks = {
            'slit': 0,
            'point': 0,
            'gisans': -100,
        },
        unit = 'mm',
    ),
)
