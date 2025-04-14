description = "neutronguide, leadblock"

group = 'lowlevel'

includes = ['nok_ref', 'zz_absoluts', 'weg01']

instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')

tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

devices = dict(
    shutter_gamma = device('nicos.devices.generic.Switcher',
        description = 'leadblock on nok1',
        moveable = 'shutter_gamma_axis',
        precision = 0.5,
        mapping = {'closed': -55,
                   'open': 0},
        fallback = 'offline',
        unit = '',
    ),
    shutter_gamma_axis = device(code_base + 'nok_support.SingleMotorNOK',
        # length: 90.0 mm
        description = 'shutter_gamma',
        motor = 'shutter_gamma_motor',
        # obs = ['shutter_gamma_analog'],
        nok_start = 198.0,
        nok_end = 288.0,
        nok_gap = 1.0,
        backlash = -2,   # is this configured somewhere?
        precision = 0.05,
        visibility = (),
    ),
    shutter_gamma_acc = device(code_base + 'accuracy.Accuracy',
         description = 'calc error Motor and poti',
         device1 = 'shutter_gamma_motor',
         device2 = 'shutter_gamma_analog',
         visibility = showcase_values['hide_acc'],
    ),
)
