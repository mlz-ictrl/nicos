description = "old"

group = 'optional'

includes = ['nok_ref', 'nokbus2']

excludes = ['beckhoff']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    nok5a_old       = device('refsans.nok_support.DoubleMotorNOK',
                            description = 'NOK5A',
                            nok_start = 2418.5,
                            nok_length = 1720.0,
                            nok_end = 4138.5,
                            nok_gap = 1.0,
                            inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                            motor_r = 'nok5ar_axis',
                            motor_s = 'nok5as_axis',
                            nok_motor = [3108.0, 3888.0],
                            backlash = -2,   # is this configured somewhere?
                            precision = 0.05,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok5ar_axis    = device('devices.generic.Axis',
                            description = 'Axis of NOK5A, reactor side',
                            motor = 'nok5ar_motor',
                            coder = 'nok5ar_motor',
                            obs = ['nok5ar_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok5ar_motor   = device('refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK5A, reactor side',
                            abslimits = (-33.04875, 61.32625),
                            userlimits = (-33.04875, 61.30375),
                            bus = 'nokbus2',     # from ipcsms_*.res
                            addr = 0x42,     # from resources.inf
                            slope = 800.0,   # FULL steps per physical unit
                            speed = 10,
                            accel = 10,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = 0,  # indivituell # from ipcsms_*.res, PLEASE FIX IT!
                            zerosteps = int(721.799 * 800),  # offset * slope
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok5ar_obs     = device('refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK5A, reactor side',
                            reference = 'nok_refb1',
                            measure = 'nok5ar_poti',
                            poly = [-43.184441, 1003.266 / 3.841],   # off, mul * 1000 / sensitivity, higher orders...
                            serial = 7545,
                            length = 250.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok5ar_poti    = device('refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK5A, reactor side',
                            tacodevice = '//%s/test/wb_b/1_4' % nethost,
                            scale = -1,  # mounted from top
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok5as_axis    = device('devices.generic.Axis',
                            description = 'Axis of NOK5A, sample side',
                            motor = 'nok5as_motor',
                            coder = 'nok5as_motor',
                            obs = ['nok5as_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok5as_motor   = device('refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK5A, sample side',
                            abslimits = (-37.49, 66.26),
                            userlimits = (-37.49, 66.25),
                            bus = 'nokbus2',     # from ipcsms_*.res
                            addr = 0x43,     # from resources.inf
                            slope = 800.0,   # FULL steps per physical unit
                            speed = 10,
                            accel = 10,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = 20.01,  # from ipcsms_*.res
                            zerosteps = int(729.99 * 800),   # offset * slope
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok5as_obs     = device('refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK5A, sample side',
                            reference = 'nok_refb1',
                            measure = 'nok5as_poti',
                            poly = [-35.263415, 1000.917 / 3.84],    # off, mul * 1000 / sensitivity, higher orders...
                            serial = 7539,
                            length = 250.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok5as_poti    = device('refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK5A, sample side',
                            tacodevice = '//%s/test/wb_b/1_1' % nethost,
                            scale = -1,  # mounted from top
                            lowlevel = True,
                           ),
)
