description = 'Single slit [slit k1] between nok6 and nok7'

group = 'optional'

devices = dict(
    # zb1 is at exit of NOK5b (so on its sample side)
    zb2_m = device('nicos.devices.generic.Axis',
        description = 'zb2 axis',
        motor = device('nicos.devices.generic.virtual.VirtualMotor',
            abslimits = (-681.9525, 568.04625),
            userlimits = (-215.69, 93.0),
            unit = 'mm',
            speed = 5.,
        ),
        precision = 0.05,
    ),
    zb2 = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        description = 'zb2 single slit at nok6 before nok7',
        motor = 'zb2_m',
        nok_start = 7591.5,
        nok_length = 6.0,
        nok_end = 7597.5,
        nok_gap = 1.0,
        masks = {
            'slit': -2,
            'point': -2,
            'gisans': -122,
        },
        unit = 'mm',
    ),
)
