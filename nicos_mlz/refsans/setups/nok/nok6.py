description = "neutronguide sideMirror noMirror"

group = 'lowlevel'

includes = ['nok_ref', 'zz_absoluts']

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
        lowlevel = True,
    ),
    nok6r_acc = device(code_base + 'nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'nok6r_motor',
         analog = 'nok6r_analog',
         lowlevel = showcase_values['hide_acc'],
         unit = 'mm'
    ),
    nok6r_analog = device(code_base + 'nok_support.NOKPosition',
        description = 'Position sensing for NOK6, reactor side',
        reference = 'nok_refb2',
        measure = 'nok6r_poti',
        # 2020-04-20 13:51:20 poly = [3.823914, 997.832 / 3.846],
        poly = [3.223914, 997.832 / 3.846],
        serial = 7538,
        length = 250.0,
        lowlevel = showcase_values['hide_poti'],
    ),
    nok6r_poti = device(code_base + 'nok_support.NOKMonitoredVoltage',
        description = 'Poti for NOK6, reactor side',
        tangodevice = tango_base + 'test/wb_b/2_1',
        scale = -1,  # mounted from top
        lowlevel = True,
    ),
    nok6s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK6, sample side',
        motor = 'nok6s_motor',
        # obs = ['nok6s_analog'],
        backlash = -0.5,
        precision = optic_values['precision_ipcsms'],
        unit = 'mm',
        lowlevel = True,
    ),
    nok6s_acc = device(code_base + 'nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'nok6s_motor',
         analog = 'nok6s_analog',
         lowlevel = showcase_values['hide_acc'],
         unit = 'mm'
    ),
    nok6s_analog = device(code_base + 'nok_support.NOKPosition',
        description = 'Position sensing for NOK6, sample side',
        reference = 'nok_refb2',
        measure = 'nok6s_poti',
        # 2020-04-20 13:51:36 poly = [16.273013, 999.674 / 3.834],
        poly = [16.003013, 999.674 / 3.834],
        serial = 7537,
        length = 250.0,
        lowlevel = showcase_values['hide_poti'],
    ),
    nok6s_poti = device(code_base + 'nok_support.NOKMonitoredVoltage',
        description = 'Poti for NOK6, sample side',
        tangodevice = tango_base + 'test/wb_b/2_2',
        scale = -1,  # mounted from top
        lowlevel = True,
    ),
)
