description = "ZB1 devices using IPC hardware"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus1']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
# masks:
# Debug (slit)
# Debug (k1)
    zb1_old        = device('refsans.nok_support.SingleMotorNOK',
                        description = 'ZB1',
                        motor = 'zb1_motor',
                        coder = 'zb1_motor',
                        obs = ['zb1_obs'],
                        nok_start = 5856.5,
                        nok_length = 13.0,
                        nok_end = 5869.5,
                        nok_gap = 1.0,
                        masks = dict(
                                     k1   = [-120.0, 0.0],
                                     slit = [0.0, 0.0],
                                    ),
                        nok_motor = 5862.5,
                        backlash = -2,   # is this configured somewhere?
                        precision = 0.05,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    zb1_motor  = device('refsans.nok_support.NOKMotorIPC',
                        description = 'IPC controlled Motor of ZB1',
                        abslimits = (-443.52875, 81.47125),
                        userlimits = (-185.0, 75.0),
                        bus = 'nokbus1',     # from ipcsms_*.res
                        addr = 0x38,     # from resources.inf
                        slope = 800.0,   # FULL steps per physical unit
                        speed = 10,
                        accel = 10,
                        confbyte = 32,
                        ramptype = 2,
                        microstep = 1,
                        refpos = 0,  # None # from ipcsms_*.res, PLEASE FIX IT!
                        zerosteps = int(682.279 * 800),  # offset * slope
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    zb1_obs    = device('refsans.nok_support.NOKPosition',
                        description = 'Position sensing for ZB1',
                        reference = 'nok_refb2',
                        measure = 'zb1_poti',
                        poly = [-144.452889, 999.589 / 1.922],   # off, mul * 1000 / sensitivity, higher orders...
                        serial = 7788,
                        length = 500.0,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    zb1_poti   = device('refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Poti for ZB1',
                        tacodevice = '//%s/test/wb_b/2_0' % nethost,
                        scale = -1,  # mounted from top
                        lowlevel = True,
                       ),
)
