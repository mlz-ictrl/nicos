description = 'backguard: after sample'

group = 'lowlevel'

tango_base = 'tango://refsanshw:10000/sample/phy_mo2/'

adjust = True

devices = dict(
    backguard = device('nicos_mlz.refsans.devices.skew_motor.SkewMotor',
        description = description + ' adjust in Expertmode',
        motor_1 = 'backguard_1',
        motor_2 = 'backguard_2',
        abslimits = (-60, 60),
        unit = 'mm',
    ),
    backguard_1 = device('nicos.devices.generic.Axis',
        description = 'Backguard axis KWS. Use this to adjust KWS-side',
        motor = 'backguard_1_m',
        precision = 0.01,
        lowlevel = not adjust,
    ),
    backguard_1_m = device('nicos.devices.tango.Motor',
        description = 'Backguard motor KWS. Use setPositon',
        tangodevice = tango_base + 'bg_1_m',
        abslimits = (-0.5, 61.0),
        lowlevel = not adjust,
        unit = 'mm',
    ),
    backguard_2 = device('nicos.devices.generic.Axis',
        description = 'Backguard axis TOFTOF. Use this to adjus TOFTOF-side',
        motor = 'backguard_2_m',
        precision = 0.01,
        lowlevel = not adjust,
    ),
    backguard_2_m = device('nicos.devices.tango.Motor',
        description = 'Backguard motor TOFTOF. Use setPositon',
        tangodevice = tango_base + 'bg_2_m',
        abslimits = (-0.5, 61.0),
        lowlevel = not adjust,
        unit = 'mm',
    ),
)
