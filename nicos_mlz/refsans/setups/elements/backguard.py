description = 'backguard: after sample'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

adjust = True

devices = dict(
    backguard = device(code_base + 'skew_motor.SkewMotor',
        description = description + ' adjust in Expertmode',
        motor_1 = 'backguard1',
        motor_2 = 'backguard2',
        abslimits = (-30.0, 30.0),
        unit = 'mm',
    ),
    backguard1 = device('nicos.devices.generic.Axis',
        description = 'Backguard axis KWS. Use this to adjust KWS-side',
        motor = 'backguard1_motor',
        precision = 0.01,
        lowlevel = not adjust,
    ),
    backguard1_motor = device('nicos.devices.tango.Motor',
        description = 'Backguard motor KWS. Use setPositon',
        tangodevice = tango_base + 'sample/phy_mo2/bg_1_m',
        abslimits = (-0.5, 61.0),
        lowlevel = not adjust,
        unit = 'mm',
    ),
    backguard2 = device('nicos.devices.generic.Axis',
        description = 'Backguard axis TOFTOF. Use this to adjust TOFTOF-side',
        motor = 'backguard2_motor',
        precision = 0.01,
        lowlevel = not adjust,
    ),
    backguard2_motor = device('nicos.devices.tango.Motor',
        description = 'Backguard motor TOFTOF. Use setPositon',
        tangodevice = tango_base + 'sample/phy_mo2/bg_2_m',
        abslimits = (-0.5, 61.0),
        lowlevel = not adjust,
        unit = 'mm',
    ),
)
