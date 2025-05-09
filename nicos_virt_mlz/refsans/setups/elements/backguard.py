description = 'backguard: after sample'

group = 'lowlevel'

devices = dict(
    backguard = device('nicos_mlz.refsans.devices.skew_motor.SkewMotor',
        description = description + ' adjust in Expert mode',
        one = 'backguard1',
        two = 'backguard2',
        abslimits = (-60, 60),
        unit = 'mm',
    ),
    backguard1 = device('nicos.devices.generic.Axis',
        description = 'Backguard axis KWS. Use this to adjust KWS-side',
        motor = 'backguard1_motor',
        precision = 0.01,
        # abslimits = (-60, 60),
        # visibility = (),
    ),
    backguard1_motor = device('nicos.devices.generic.VirtualMotor',
        description = 'Backguard motor KWS. Use setPositon',
        abslimits = (-61.0, 61.0),
        speed = 1,
        unit = 'mm',
        curvalue = -5,
        visibility = {'metadata', },
    ),
    backguard2 = device('nicos.devices.generic.Axis',
        description = 'Backguard axis TOFTOF. Use this to adjust TOFTOF-side',
        precision = 0.01,
        motor = 'backguard2_motor',
        # abslimits = (-60, 60),
        # visibility = (),
    ),
    backguard2_motor = device('nicos.devices.generic.VirtualMotor',
        description = 'Backguard motor TOFTOF. Use setPositon',
        abslimits = (-61.0, 61.0),
        speed = 1,
        unit = 'mm',
        curvalue = -5,
        visibility = {'metadata', },
    ),
)
