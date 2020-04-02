description = "neutronguide sideMirror noMirror"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus4', 'nokbus3']

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
            'ng': optic_values['ng'],
            'rc': optic_values['ng'],
            'vc': optic_values['vc'],
            'fc': optic_values['fc'],
        },
    ),
    nok6r_axis = device('nicos.devices.generic.Axis',
        description = 'Axis of NOK6, reactor side',
        motor = 'nok6r_motor',
        # obs = ['nok6r_analog'],
        backlash = -0.5,
        precision = 0.0,
        unit = 'mm',
        lowlevel = True,
    ),
    nok6r_motor = device(code_base + 'ipc.NOKMotorIPC',
        description = 'IPC controlled Motor of NOK6, reactor side nasty!',
        abslimits = (-66.2, 96.59125),
        bus = 'nokbus4',
        addr = 0x63,
        slope = 2000.0,
        speed = 100,
        accel = 100,
        confbyte = 48,
        ramptype = 2,
        microstep = 1,
        refpos = 45.51,
        zerosteps = int(704.638 * 800),
        lowlevel = showcase_values['hide_poti'],
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
        poly = [3.823914, 997.832 / 3.846],
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
        precision = 0.0,
        unit = 'mm',
        lowlevel = True,
    ),
    nok6s_motor = device(code_base + 'ipc.NOKMotorIPC',
        description = 'IPC controlled Motor of NOK6, sample side',
        abslimits = (-81.0, 110.875),
        bus = 'nokbus3',
        addr = 0x51,
        slope = 800.0,
        speed = 40,
        accel = 40,
        confbyte = 48,
        ramptype = 2,
        microstep = 1,
        refpos = 46.67,
        zerosteps = int(703.5 * 800),
        lowlevel = showcase_values['hide_poti'],
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
        poly = [16.273013, 999.674 / 3.834],
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
