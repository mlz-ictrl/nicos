description = "neutronguide sideMirror noMirror"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus3']
instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')

tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

devices = dict(
    nok7 = device(code_base + 'nok_support.DoubleMotorNOK',
        # length: 1190.0 mm
        description = 'NOK7',
        fmtstr = '%.2f, %.2f',
        nok_start = 7665.5,
        nok_end = 8855.5,
        nok_gap = 1.0,
        inclinationlimits = (-100, 100),
        motor_r = 'nok7r_axis',
        motor_s = 'nok7s_axis',
        nok_motor = [7915.0, 8605.0],
        precision = 0.0,
        masks = {
            'ng': optic_values['ng'],
            'rc': optic_values['ng'],
            'vc': optic_values['vc'],
            'fc': optic_values['fc'],
        },
    ),
    nok7r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK7, reactor side',
        motor = 'nok7r_motor',
        # obs = ['nok7r_analog'],
        backlash = -0.5,
        precision = 0.0,
        unit = 'mm',
        lowlevel = True,
    ),
    nok7r_motor = device(code_base + 'ipc.NOKMotorIPC',
        description = 'IPC controlled Motor of NOK7, reactor side',
        abslimits = (-89.475, 116.1),
        bus = 'nokbus3',
        addr = 0x52,
        slope = 800.0,
        speed = 10,
        accel = 10,
        confbyte = 48,
        ramptype = 2,
        microstep = 1,
        refpos = 62.4,
        zerosteps = int(687.6 * 800),
        lowlevel = showcase_values['hide_poti'],
    ),

    nok7r_acc = device(code_base + 'nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'nok7r_motor',
         analog = 'nok7r_analog',
         lowlevel = showcase_values['hide_acc'],
         unit = 'mm'
    ),

    nok7r_analog = device(code_base + 'nok_support.NOKPosition',
        description = 'Position sensing for NOK7, reactor side',
        reference = 'nok_refc1',
        measure = 'nok7r_poti',
        poly = [16.262881, 1001.504 / 3.843],
        serial = 7540,
        length = 250.0,
        lowlevel = showcase_values['hide_poti'],
    ),

    nok7r_poti = device(code_base + 'nok_support.NOKMonitoredVoltage',
        description = 'Poti for NOK7, reactor side',
        tangodevice = tango_base + 'test/wb_c/1_0',
        scale = -1,  # mounted from top
        lowlevel = True,
    ),

    nok7s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK7, sample side',
        motor = 'nok7s_motor',
        # obs = ['nok7s_analog'],
        backlash = -0.5,
        precision = 0.0,
        unit = 'mm',
        lowlevel = True,
    ),
    nok7s_motor = device(code_base + 'ipc.NOKMotorIPC',
        description = 'IPC controlled Motor of NOK7, sample side',
        abslimits = (-96.94, 125.56),
        bus = 'nokbus3',
        addr = 0x53,
        slope = 800.0,
        speed = 10,
        accel = 10,
        confbyte = 48,
        ramptype = 2,
        microstep = 1,
        refpos = 66.84,
        zerosteps = int(683.19 * 800),
        lowlevel = showcase_values['hide_poti'],
    ),

    nok7s_acc = device(code_base + 'nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'nok7s_motor',
         analog = 'nok7s_analog',
         lowlevel = showcase_values['hide_acc'],
         unit = 'mm'
    ),

    nok7s_analog = device(code_base + 'nok_support.NOKPosition',
        description = 'Position sensing for NOK7, sample side',
        reference = 'nok_refc1',
        measure = 'nok7s_poti',
        poly = [18.40, 1000.00 / 3.841],
        serial = 7546,
        length = 250.0,
        lowlevel = showcase_values['hide_poti'],
    ),

    nok7s_poti = device(code_base + 'nok_support.NOKMonitoredVoltage',
        description = 'Poti for NOK7, sample side',
        tangodevice = tango_base + 'test/wb_c/1_5',
        scale = -1,  # mounted from top
        lowlevel = True,
    ),
)
