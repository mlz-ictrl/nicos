description = 'Slit ZB1 using beckhoff controllers'

group = 'lowlevel'

lprecision = 0.01

devices = dict(
    zb1 = device('nicos_mlz.refsans.devices.slits.SingleSlit',
        description = 'zb1, singleslit at nok5b before nok6',
        unit = 'mm',
        motor = 'zb1_a',
        offset = 0.0,
        nok_start = 5856.5,
        nok_length = 13,
        nok_end = 5862.5,
        nok_gap = 1,
        # nok_motor = 5862.5,
        masks = {
            'slit':    0,
            'point':   0,
            'gisans':  -110,
        },
    ),
    zb1_a = device('nicos.devices.generic.Axis',
        description = 'zb1 axis',
        motor = device('nicos.devices.generic.VirtualMotor',
            unit = 'mm',
            abslimits = (-178.9,  53.9),
            speed = 1.,
        ),
        precision = lprecision,
        maxtries = 3,
        lowlevel = True,
    ),
)
