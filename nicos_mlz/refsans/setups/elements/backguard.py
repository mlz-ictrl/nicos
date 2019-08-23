description = 'backguard: after sample'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base']

adjust = True

devices = dict(
    backguard = device('nicos_mlz.refsans.devices.skew_motor.SkewMotor',
        description = description + ' adjust in Expertmode',
        motor_1 = 'backguard_1',
        motor_2 = 'backguard_2',
        abslimits = (-30.0, 30.0),
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
        tangodevice = tango_base + 'sample/phy_mo2/bg_1_m',
        abslimits = (-0.5, 61.0),
        lowlevel = not adjust,
        unit = 'mm',
    ),
    backguard_2 = device('nicos.devices.generic.Axis',
        description = 'Backguard axis TOFTOF. Use this to adjust TOFTOF-side',
        motor = 'backguard_2_m',
        precision = 0.01,
        lowlevel = not adjust,
    ),
    backguard_2_m = device('nicos.devices.tango.Motor',
        description = 'Backguard motor TOFTOF. Use setPositon',
        tangodevice = tango_base + 'sample/phy_mo2/bg_2_m',
        abslimits = (-0.5, 61.0),
        lowlevel = not adjust,
        unit = 'mm',
    ),
)
