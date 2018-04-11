description = 'neutronguide, leadblock'

group = 'lowlevel'

devices = dict(
    shutter_gamma = device('nicos.devices.generic.Switcher',
        description = 'leadblock on nok1',
        moveable = 'nok1',
        precision = 0.5,
        mapping = {'closed': -55, 'open': 0},
        fallback = 'offline',
    ),
    nok1 = device('nicos_mlz.refsans.devices.nok_support.SingleMotorNOK',
        description = 'shutter_gamma NOK1',
        motor = 'nok1_motor',
        coder = 'nok1_motor',
        nok_start = 198.0,
        nok_length = 90.0,
        nok_end = 288.0,
        nok_gap = 1.0,
        backlash = -2,
        precision = 0.05,
        lowlevel = True,
    ),
    nok1_motor = device('nicos.devices.generic.VirtualMotor',
        description = 'IPC controlled Motor of NOK1',
        abslimits = (-56.119, 1.381),
        lowlevel = True,
        unit = 'mm',
    ),
)
