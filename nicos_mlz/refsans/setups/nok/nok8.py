description = "neutronguide sideMirror noMirror"

group = 'lowlevel'

includes = ['nok_ref', 'zz_absoluts']
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
        lowlevel = True,
    ),
    nok8r_acc = device(code_base + 'nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'nok8r_motor',
         analog = 'nok8r_analog',
         lowlevel = showcase_values['hide_acc'],
         unit = 'mm'
    ),
    nok8r_analog = device(code_base + 'nok_support.NOKPosition',
        description = 'Position sensing for NOK8, reactor side',
        reference = 'nok_refc1',
        measure = 'nok8r_poti',
        # 2020-04-24 09:37:43 poly = [9.418174, 1001.53 / 3.85],
        poly = [9.69, 1001.53 / 3.85],
        serial = 6508,
        length = 250.0,
        lowlevel = showcase_values['hide_poti'],
    ),
    nok8r_poti = device(code_base + 'nok_support.NOKMonitoredVoltage',
        description = 'Poti for NOK8, reactor side',
        tangodevice = tango_base + 'test/wb_c/1_4',
        scale = -1,
        lowlevel = True,
    ),
    nok8s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK8, sample side',
        motor = 'nok8s_motor',
        # obs = ['nok8s_analog'],
        backlash = -0.5,
        precision = optic_values['precision_ipcsms'],
        unit = 'mm',
        lowlevel = True,
    ),
    nok8s_acc = device(code_base + 'nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'nok8s_motor',
         analog = 'nok8s_analog',
         lowlevel = showcase_values['hide_acc'],
         unit = 'mm'
    ),
    nok8s_analog = device(code_base + 'nok_support.NOKPosition',
        description = 'Position sensing for NOK8, sample side',
        reference = 'nok_refc2',
        measure = 'nok8s_poti',
        # 2020-04-24 09:38:09 poly = [7.252627, 998.722 / 3.85],
        poly = [7.512, 998.722 / 3.85],
        serial = 6511,
        length = 250.0,
        lowlevel = showcase_values['hide_poti'],
    ),
    nok8s_poti = device(code_base + 'nok_support.NOKMonitoredVoltage',
        description = 'Poti for NOK8, sample side',
        tangodevice = tango_base + 'test/wb_c/2_0',
        scale = -1,  # mounted from top
        lowlevel = True,
    ),
)
