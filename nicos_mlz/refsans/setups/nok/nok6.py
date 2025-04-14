description = "neutronguide sideMirror noMirror"

group = 'lowlevel'

includes = ['nok_ref', 'zz_absoluts', 'weg02']

instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')

tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

devices = dict(
    nok6 = device(code_base + 'nok_support.DoubleMotorNOK',
        # length: 1720.0 mm
        description = 'NOK6',
        fmtstr = '%.2f, %.2f',
        nok_start = 5887.5,
        nok_end = 7607.5,
        nok_gap = 1.0,
        inclinationlimits = (-100, 100),
        motor_r = 'nok6r_axis',
        motor_s = 'nok6s_axis',
        nok_motor = [6137.0, 7357.0],
        precision = 0.0,
        masks = {
            'ng': -0.5 + optic_values['ng'],  # 2021-03-18 11:52:07 TheoMH 0.0
            'rc': -0.5 + optic_values['ng'],  # 2021-03-18 11:52:07 TheoMH 0.0
            'vc': -0.5 + optic_values['vc'],  # 2021-03-18 11:52:07 TheoMH 0.0
            'fc': -0.5 + optic_values['fc'],  # 2021-03-18 11:52:07 TheoMH 0.0
        },
    ),
    nok6r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK6, reactor side',
        motor = 'nok6r_motor',
        # obs = ['nok6r_analog'],
        backlash = -0.5,
        precision = optic_values['precision_ipcsms'],
        unit = 'mm',
        visibility = (),
    ),
    nok6r_acc = device(code_base + 'accuracy.Accuracy',
         description = 'calc error Motor and poti',
         device1 = 'nok6r_motor',
         device2 = 'nok6r_analog',
         visibility = showcase_values['hide_acc'],
    ),
    nok6s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK6, sample side',
        motor = 'nok6s_motor',
        # obs = ['nok6s_analog'],
        backlash = -0.5,
        precision = optic_values['precision_ipcsms'],
        unit = 'mm',
        visibility = (),
    ),
    nok6s_acc = device(code_base + 'accuracy.Accuracy',
         description = 'calc error Motor and poti',
         device1 = 'nok6s_motor',
         device2 = 'nok6s_analog',
         visibility = showcase_values['hide_acc'],
    ),
)
