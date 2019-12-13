description = "neutronguide, leadblock"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus1']
hide_poti = True

tango_base = 'tango://refsanshw:10000/test/'

devices = dict(
    shutter_gamma = device('nicos.devices.generic.Switcher',
        description = 'leadblock on nok1',
        moveable = 'nok1',
        precision = 0.5,
        mapping = {'closed': -55,
                   'open': 0},
        fallback = 'offline',
        unit = '',
    ),
    nok1 = device('nicos_mlz.refsans.devices.nok_support.SingleMotorNOK',
        # length: 90.0 mm
        description = 'shutter_gamma NOK1',
        motor = 'nok1_motor',
        # obs = ['nok1_obs'],
        nok_start = 198.0,
        nok_end = 288.0,
        nok_gap = 1.0,
        backlash = -2,   # is this configured somewhere?
        precision = 0.05,
        lowlevel = True,
    ),

    # generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok1_motor = device('nicos_mlz.refsans.devices.ipc.NOKMotorIPC',
        description = 'IPC controlled Motor of NOK1',
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
    nok1_obs = device('nicos_mlz.refsans.devices.nok_support.NOKPosition',
        description = 'Position sensing for NOK1',
        reference = 'nok_refa1',
        measure = 'nok1_poti',
        poly = [-13.748035, 996.393 / 3.856],    # off, mul * 1000 / sensitivity, higher orders...
        serial = 6505,
        length = 250.0,
        lowlevel = True,
    ),

    # generated from global/inf/poti_tracing.inf
    nok1_poti = device('nicos_mlz.refsans.devices.nok_support.NOKMonitoredVoltage',
        description = 'Poti for NOK1',
        tangodevice = tango_base + 'wb_a/1_0',
        scale = 1,   # mounted from bottom
        lowlevel = True,
    ),

    nok1_acc = device('nicos_mlz.refsans.devices.nok_support.MotorEncoderDifference',
         description = 'calc error Motor and poti',
         motor = 'nok1_motor',
         analog = 'nok1_obs',
         lowlevel = hide_poti,
         unit = 'mm'
    ),
)
