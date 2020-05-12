description = "neutronguide sideMirror noMirror"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus3', 'nokbus4']
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
            'ng': optic_values['ng'],
            'rc': optic_values['ng'],
            'vc': optic_values['vc'],
            'fc': optic_values['fc'],
        }
    ),
    nok9r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK9, reactor side',
        motor = 'nok9r_motor',
        # obs = ['nok9r_analog'],
        backlash = -0.5,
        precision = 0.0,
        unit = 'mm',
        lowlevel = True,
    ),
    nok9r_motor = device(code_base + 'ipc.NOKMotorIPC',
        description = 'IPC controlled Motor of NOK9, reactor side',
        abslimits = (-112.03425, 142.95925),
        bus = 'nokbus3',
        addr = 0x56,
        slope = 800.0,
        speed = 1,
        accel = 1,
        confbyte = 48,
        ramptype = 2,
        microstep = 1,
        refpos = 103.086,
        lowlevel = showcase_values['hide_poti'],
        zerosteps = int(647.034 * 800),
    ),
    nok9r_acc = device(code_base + 'nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'nok9r_motor',
         analog = 'nok9r_analog',
         lowlevel = showcase_values['hide_acc'],
         unit = 'mm'
    ),

    nok9r_analog = device(code_base + 'nok_support.NOKPosition',
        description = 'Position sensing for NOK9, reactor side',
        reference = 'nok_refc2',
        measure = 'nok9r_poti',
        # MP 2019-06-11 09:39:53 poly = [-99.195992, 1000.37 / 1.922],
        poly = [-99.965992, 1000.37 / 1.922],
        serial = 7779,
        length = 500.0,
        lowlevel = showcase_values['hide_poti'],
    ),

    nok9r_poti = device(code_base + 'nok_support.NOKMonitoredVoltage',
        description = 'Poti for NOK9, reactor side',
        tangodevice = tango_base + 'test/wb_c/2_3',
        scale = -1,  # mounted from top
        lowlevel = True,
    ),

    nok9s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK9, sample side',
        motor = 'nok9s_motor',
        # obs = ['nok9s_analog'],
        backlash = -0.5,
        precision = 0.0,
        unit = 'mm',
        lowlevel = True,
    ),
    nok9s_motor = device(code_base + 'ipc.NOKMotorIPC',
        description = 'IPC controlled Motor of NOK9, sample side',
        abslimits = (-114.51425, 142.62775),
        bus = 'nokbus4',
        addr = 0x61,
        slope = 800.0,
        speed = 1,
        accel = 1,
        confbyte = 48,
        ramptype = 2,
        microstep = 1,
        refpos = 86.749,
        zerosteps = int(663.601 * 800),
        lowlevel = showcase_values['hide_poti'],
    ),

    nok9s_acc = device(code_base + 'nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'nok9s_motor',
         analog = 'nok9s_analog',
         lowlevel = showcase_values['hide_acc'],
         unit = 'mm'
    ),

    nok9s_analog = device(code_base + 'nok_support.NOKPosition',
        description = 'Position sensing for NOK9, sample side',
        reference = 'nok_refc2',
        measure = 'nok9s_poti',
        # MP 2019-06-11 09:40:44 poly = [80.372504, 998.695 / 1.919],
        poly = [79.372504, 998.695 / 1.919],
        serial = 7789,
        length = 500.0,
        lowlevel = showcase_values['hide_poti'],
    ),

    nok9s_poti = device(code_base + 'nok_support.NOKMonitoredVoltage',
        description = 'Poti for NOK9, sample side',
        tangodevice = tango_base + 'test/wb_c/2_4',
        scale = -1,  # mounted from top
        lowlevel = True,
    ),
)
