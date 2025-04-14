description = "neutronguide sideMirror noMirror"

group = 'lowlevel'

includes = ['nok_ref', 'zz_absoluts', 'weg03']
instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')

tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

devices = dict(
    nok8 = device(code_base + 'nok_support.DoubleMotorNOK',
        # length: 880.0 mm
        description = 'NOK8',
        fmtstr = '%.2f, %.2f',
        nok_start = 8870.5,
        nok_end = 9750.5,
        nok_gap = 1.0,
        inclinationlimits = (-30 , 30),
        motor_r = 'nok8r_axis',
        motor_s = 'nok8s_axis',
        nok_motor = [9120.0, 9500.0],
        precision = 0.0,
        masks = {
            'ng': -0.75 + optic_values['ng'],  # 2021-03-18 11:55:55 Theo MH 0.0
            'rc': -0.75 + optic_values['ng'],  # 2021-03-18 11:55:55 Theo MH 0.0
            'vc': -0.75 + optic_values['vc'],  # 2021-03-18 11:55:55 Theo MH 0.0
            'fc': -1.75 + optic_values['fc'],  # 2021-03-18 11:55:55 Theo MH 0.0
        },
    ),
    nok8r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK8, reactor side',
        motor = 'nok8r_motor',
        # obs = ['nok8r_analog'],
        backlash = -0.5,
        precision = optic_values['precision_ipcsms'],
        unit = 'mm',
        visibility = (),
    ),
    nok8r_acc = device(code_base + 'accuracy.Accuracy',
         description = 'calc error Motor and poti',
         device1 = 'nok8r_motor',
         device2 = 'nok8r_analog',
         visibility = showcase_values['hide_acc'],
    ),
    nok8s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK8, sample side',
        motor = 'nok8s_motor',
        # obs = ['nok8s_analog'],
        backlash = -0.5,
        precision = optic_values['precision_ipcsms'],
        unit = 'mm',
        visibility = (),
    ),
    nok8s_acc = device(code_base + 'accuracy.Accuracy',
         description = 'calc error Motor and poti',
         device1 = 'nok8s_motor',
         device2 = 'nok8s_analog',
         visibility = showcase_values['hide_acc'],
    ),
)
