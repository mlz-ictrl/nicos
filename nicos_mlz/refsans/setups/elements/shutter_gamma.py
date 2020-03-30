description = "neutronguide, leadblock"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus1']
instrument_values = configdata('instrument.values')
showcase_values = configdata('cf_showcase.showcase_values')

tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base'] + 'nok_support.'

devices = dict(
    shutter_gamma = device('nicos.devices.generic.Switcher',
        description = 'leadblock on nok1',
        moveable = 'shutter_gamma_switcher',
        precision = 0.5,
        mapping = {'closed': -55,
                   'open': 0},
        fallback = 'offline',
        unit = '',
    ),
    shutter_gamma_switcher = device(code_base + 'SingleMotorNOK',
        # length: 90.0 mm
        description = 'shutter_gamma',
        motor = 'shutter_gamma_motor',
        # obs = ['shutter_gamma_analog'],
        nok_start = 198.0,
        nok_end = 288.0,
        nok_gap = 1.0,
        backlash = -2,   # is this configured somewhere?
        precision = 0.05,
        lowlevel = True,
    ),

    # generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    shutter_gamma_motor = device('nicos_mlz.refsans.devices.ipc.NOKMotorIPC',
        description = 'IPC controlled Motor of shutter_gamma',
        abslimits = (-56.119, 1.381),
        userlimits = (-56.119, 1.381),
        bus = 'nokbus1',     # from ipcsms_*.res
        addr = 0x31,     # from resources.inf
        slope = 2000.0,  # FULL steps per physical unit
        speed = 10,
        accel = 10,
        confbyte = 48,
        ramptype = 2,
        microstep = 1,
        refpos = -14.729,    # from ipcsms_*.res
        zerosteps = int(264.619 * 2000),     # offset * slope
        lowlevel = True,
    ),

    # generated from global/inf/poti_tracing.inf
    shutter_gamma_analog = device(code_base + 'NOKPosition',
        description = 'Position sensing for shutter_gamma',
        reference = 'nok_refa1',
        measure = 'shutter_gamma_poti',
        poly = [-13.748035, 996.393 / 3.856],    # off, mul * 1000 / sensitivity, higher orders...
        serial = 6505,
        length = 250.0,
        lowlevel = True,
    ),

    # generated from global/inf/poti_tracing.inf
    shutter_gamma_poti = device(code_base + 'NOKMonitoredVoltage',
        description = 'Poti for shutter_gamma',
        tangodevice = tango_base + 'test/wb_a/1_0',
        scale = 1,   # mounted from bottom
        lowlevel = True,
    ),

    shutter_gamma_acc = device(code_base + 'MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'shutter_gamma_motor',
         analog = 'shutter_gamma_analog',
         lowlevel = showcase_values['hide_poti'],
         unit = 'mm'
    ),
)
