description = "neutronguide sideMirror noMirror"

group = 'lowlevel'

includes = ['nok_ref', 'zz_absoluts', 'weg03']
instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')

tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

devices = dict(
    nok9 = device(code_base + 'nok_support.DoubleMotorNOK',
        # length: 840.0 mm
        description = 'NOK9',
        nok_start = 9773.5,
        fmtstr = '%.2f, %.2f',
        nok_end = 10613.5,
        nok_gap = 1.0,
        inclinationlimits = (-30 , 30),
        motor_r = 'nok9r_axis',
        motor_s = 'nok9s_axis',
        nok_motor = [10023.5, 10362.7],
        precision = 0.0,
        masks = {
            'ng': -0.75 + optic_values['ng'],  # 2021-03-18 11:55:55 Theo MH 0.0
            'rc': -0.75 + optic_values['ng'],  # 2021-03-18 11:55:55 Theo MH 0.0
            'vc': -0.75 + optic_values['vc'],  # 2021-03-18 11:55:55 Theo MH 0.0
            'fc': -3.25 + optic_values['fc'],  # 2021-03-18 11:55:55 Theo MH 0.0
        }
    ),
    nok9r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK9, reactor side',
        motor = 'nok9r_motor',
        # obs = ['nok9r_analog'],
        backlash = -0.5,
        precision = optic_values['precision_ipcsms'],
        unit = 'mm',
        visibility = (),
    ),
    nok9r_acc = device(code_base + 'accuracy.Accuracy',
         description = 'calc error Motor and poti',
         device1 = 'nok9r_motor',
         device2 = 'nok9r_analog',
         visibility = showcase_values['hide_acc'],
    ),
    nok9s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK9, sample side',
        motor = 'nok9s_motor',
        # obs = ['nok9s_analog'],
        backlash = -0.5,
        precision = optic_values['precision_ipcsms'],
        unit = 'mm',
        visibility = (),
    ),
    nok9s_acc = device(code_base + 'accuracy.Accuracy',
         description = 'calc error Motor and poti',
         device1 = 'nok9s_motor',
         device2 = 'nok9s_analog',
         visibility = showcase_values['hide_acc'],
    ),
)
