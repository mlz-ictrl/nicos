description = "neutronguide, radialcollimator"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus1']
instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')
optic_values = configdata('cf_optic.optic_values')

tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

devices = dict(
    nok3 = device(code_base + 'nok_support.DoubleMotorNOK',
        # length: 600.0 mm
        description = 'NOK3',
        fmtstr = '%.2f, %.2f',
        nok_start = 680.0,
        nok_end = 1280.0,
        nok_gap = 1.0,
        inclinationlimits = (-20, 20),
        motor_r = 'nok3r_axis',
        motor_s = 'nok3s_axis',
        nok_motor = [831.0, 1131.0],
        precision = 0.0,
        masks = {
            'ng': optic_values['ng'],
            'rc': optic_values['rc'],
            'vc': optic_values['ng'],
            'fc': optic_values['ng'],
        },
    ),
    nok3r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK3, reactor side',
        motor = 'nok3r_motor',
        # obs = ['nok3r_analog'],
        backlash = -0.5,
        precision = 0.0,
        unit = 'mm',
        lowlevel = True,
    ),
    nok3r_motor = device(code_base + 'ipc.NOKMotorIPC',
        description = 'IPC controlled Motor of NOK3, reactor side',
        abslimits = (-21.967, 47.783),
        bus = 'nokbus1',
        addr = 0x34,
        slope = 2000.0,
        speed = 10,
        accel = 10,
        confbyte = 48,
        ramptype = 2,
        microstep = 1,
        refpos = 20.6225,
        zerosteps = int(229.467 * 2000),
        lowlevel = showcase_values['hide_poti'],
    ),

    nok3r_acc = device(code_base + 'nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'nok3r_motor',
         analog = 'nok3r_analog',
         lowlevel = showcase_values['hide_acc'],
         unit = 'mm'
    ),

    nok3r_analog = device(code_base + 'nok_support.NOKPosition',
        description = 'Position sensing for NOK3, reactor side',
        reference = 'nok_refa1',
        measure = 'nok3r_poti',
        poly = [21.830175, 997.962 / 3.846],
        serial = 6507,
        length = 250.0,
        lowlevel = showcase_values['hide_poti'],
    ),

    nok3r_poti = device(code_base + 'nok_support.NOKMonitoredVoltage',
        description = 'Poti for NOK3, reactor side',
        tangodevice = tango_base + 'test/wb_a/1_3',
        scale = 1,   # mounted from bottom
        lowlevel = True,
    ),

    nok3s_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK3, sample side',
        motor = 'nok3s_motor',
        # obs = ['nok3s_analog'],
        backlash = -0.5,
        precision = 0.0,
        unit = 'mm',
        lowlevel = True,
    ),
    nok3s_motor = device(code_base + 'ipc.NOKMotorIPC',
        description = 'IPC controlled Motor of NOK3, sample side',
        abslimits = (-20.9435, 40.8065),
        bus = 'nokbus1',
        addr = 0x35,
        slope = 2000.0,
        speed = 10,
        accel = 10,
        confbyte = 48,
        ramptype = 2,
        microstep = 1,
        refpos = 9.444,
        zerosteps = int(240.694 * 2000),
        lowlevel = showcase_values['hide_poti'],
    ),

    nok3s_acc = device(code_base + 'nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'nok3s_motor',
         analog = 'nok3s_analog',
         lowlevel = showcase_values['hide_acc'],
         unit = 'mm'
    ),

    nok3s_analog = device(code_base + 'nok_support.NOKPosition',
        description = 'Position sensing for NOK3, sample side',
        reference = 'nok_refa1',
        measure = 'nok3s_poti',
        poly = [10.409698, 1003.196 / 3.854],
        serial = 6506,
        length = 250.0,
        lowlevel = showcase_values['hide_poti'],
    ),

    nok3s_poti = device(code_base + 'nok_support.NOKMonitoredVoltage',
        description = 'Poti for NOK3, sample side',
        tangodevice = tango_base + 'test/wb_a/1_4',
        scale = 1,   # mounted from bottom
        lowlevel = True,
    ),
)
