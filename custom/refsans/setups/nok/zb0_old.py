description = "ZB0 devices using IPC hardware"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus1']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
# masks:
# Debug (slit)
# Debug (k1)
    zb0_old        = device('nicos_mlz.refsans.nok_support.SingleMotorNOK',
                        description = 'ZB0',
                        motor = 'zb0_motor',
                        coder = 'zb0_motor',
                        obs = ['zb0_obs'],
                        nok_start = 4121.5,
                        nok_length = 13.0,
                        nok_end = 4134.5,
                        nok_gap = 1.0,
                        masks = dict(
                                     k1   = [-110.0, 0.0],
                                     slit = [0.0, 0.0],
                                    ),
                        nok_motor = 4128.5,
                        backlash = -2,   # is this configured somewhere?
                        precision = 0.05,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    zb0_motor  = device('nicos_mlz.refsans.nok_support.NOKMotorIPC',
                        description = 'IPC controlled Motor of ZB0',
                        abslimits = (-180.815, 69.185),
                        userlimits = (-180.815, 69.08375),
                        bus = 'nokbus1',     # from ipcsms_*.res
                        addr = 0x37,     # from resources.inf
                        slope = 800.0,   # FULL steps per physical unit
                        speed = 10,
                        accel = 10,
                        confbyte = 32,
                        ramptype = 2,
                        microstep = 1,
                        refpos = 0,  # None # from ipcsms_*.res, PLEASE FIX IT!
                        zerosteps = int(703.315 * 800),  # offset * slope
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    zb0_obs    = device('nicos_mlz.refsans.nok_support.NOKPosition',
                        description = 'Position sensing for ZB0',
                        reference = 'nok_refb1',
                        measure = 'zb0_poti',
                        poly = [-140.496936, 1001.42 / 1.918],   # off, mul * 1000 / sensitivity, higher orders...
                        serial = 7780,
                        length = 500.0,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    zb0_poti   = device('nicos_mlz.refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Poti for ZB0',
                        tacodevice = '//%s/test/wb_b/1_2' % nethost,
                        scale = -1,  # mounted from top
                        lowlevel = True,
                       ),
)
