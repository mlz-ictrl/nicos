description = "DoubleSlit [slit k1] between nok8 and nok9"

group = 'optional'

includes = ['nok_ref', 'nokbus4']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
# masks:
# 2010-06-15 10:42:09 (slit)
# 12.01.2010 10:35:26 (k1)
    bs1        = device('refsans.nok_support.DoubleMotorNOK',
                        description = 'BS1',
                        nok_start = 9764.5,
                        nok_length = 6.0,
                        nok_end = 9770.5,
                        nok_gap = 18.0,
                        inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                        masks = dict(
                                     k1   = [-40.0, 0.0, -1.83, 0.0],
                                     slit = [0.0, 0.0, -0.67, -0.89],
                                    ),
                        motor_r = 'bs1r_axis',
                        motor_s = 'bs1s_axis',
                        nok_motor = [9764.75, 9770.25],
                        backlash = -2,   # is this configured somewhere?
                        precision = 0.05,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    bs1r_axis  = device('devices.generic.Axis',
                        description = 'Axis of BS1, reactor side',
                        motor = 'bs1r_motor',
                        coder = 'bs1r_motor',
                        obs = ['bs1r_obs'],
                        backlash = 0,
                        precision = 0.05,
                        unit = 'mm',
                        lowlevel = True,
                       ),

    bs1_srll = device('devices.taco.DigitalInput',
                      description = 'Device test/bs1/srll of Server ipcsmsserver bs1',
                      tacodevice = '//%s/test/bs1/srll' % nethost,
                     ),

    bs1_srhl = device('devices.taco.DigitalInput',
                      description = 'Device test/bs1/srhl of Server ipcsmsserver bs1',
                      tacodevice = '//%s/test/bs1/srhl' % nethost,
                     ),

    bs1_srref = device('devices.taco.DigitalInput',
                       description = 'Device test/bs1/srref of Server ipcsmsserver bs1',
                       tacodevice = '//%s/test/bs1/srref' % nethost,
                      ),

    bs1_srrel = device('devices.taco.DigitalInput',
                       description = 'Device test/bs1/srrel of Server ipcsmsserver bs1',
                       tacodevice = '//%s/test/bs1/srrel' % nethost,
                      ),

    bs1_srsll = device('devices.taco.DigitalInput',
                       description = 'Device test/bs1/srsll of Server ipcsmsserver bs1',
                       tacodevice = '//%s/test/bs1/srsll' % nethost,
                      ),

    bs1_srshl = device('devices.taco.DigitalInput',
                       description = 'Device test/bs1/srshl of Server ipcsmsserver bs1',
                       tacodevice = '//%s/test/bs1/srshl' % nethost,
                      ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    bs1r_motor = device('refsans.nok_support.NOKMotorIPC',
                        description = 'IPC controlled Motor of BS1, reactor side',
                        abslimits = (-323.075, 458.17375),
                        userlimits = (-178.0, -0.7),
                        bus = 'nokbus4',     # from ipcsms_*.res
                        addr = 0x67,     # from resources.inf
                        slope = 800.0,   # FULL steps per physical unit
                        speed = 5,
                        accel = 5,
                        confbyte = 32,
                        ramptype = 2,
                        microstep = 1,
                        refpos = -41.8,  # from ipcsms_*.res
                        zerosteps = int(791.825 * 800),  # offset * slope
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    bs1r_obs   = device('refsans.nok_support.NOKPosition',
                        description = 'Position sensing for BS1, reactor side',
                        reference = 'nok_refc2',
                        measure = 'bs1r_poti',
                        poly = [-104.210515, 998.068 / 3.835],   # off, mul * 1000 / sensitivity, higher orders...
                        serial = 7542,
                        length = 250.0,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    bs1r_poti  = device('refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Poti for BS1, reactor side',
                        tacodevice = '//%s/test/wb_c/2_1' % nethost,
                        scale = 1,   # mounted from bottom
                        lowlevel = True,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    bs1s_axis  = device('devices.generic.Axis',
                        description = 'Axis of BS1, sample side',
                        motor = 'bs1s_motor',
                        coder = 'bs1s_motor',
                        obs = ['bs1s_obs'],
                        backlash = 0,
                        precision = 0.05,
                        unit = 'mm',
                        lowlevel = True,
                       ),

    bs1_ssll = device('devices.taco.DigitalInput',
                      description = 'Device test/bs1/ssll of Server ipcsmsserver bs1',
                      tacodevice = '//%s/test/bs1/ssll' % nethost,
                     ),

    bs1_sshl = device('devices.taco.DigitalInput',
                      description = 'Device test/bs1/sshl of Server ipcsmsserver bs1',
                      tacodevice = '//%s/test/bs1/sshl' % nethost,
                     ),

    bs1_ssref = device('devices.taco.DigitalInput',
                       description = 'Device test/bs1/ssref of Server ipcsmsserver bs1',
                       tacodevice = '//%s/test/bs1/ssref' % nethost,
                      ),

    bs1_ssrel = device('devices.taco.DigitalInput',
                       description = 'Device test/bs1/ssrel of Server ipcsmsserver bs1',
                       tacodevice = '//%s/test/bs1/ssrel' % nethost,
                      ),

    bs1_sssll = device('devices.taco.DigitalInput',
                       description = 'Device test/bs1/sssll of Server ipcsmsserver bs1',
                       tacodevice = '//%s/test/bs1/sssll' % nethost,
                      ),

    bs1_ssshl = device('devices.taco.DigitalInput',
                       description = 'Device test/bs1/ssshl of Server ipcsmsserver bs1',
                       tacodevice = '//%s/test/bs1/ssshl' % nethost,
                      ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    bs1s_motor = device('refsans.nok_support.NOKMotorIPC',
                        description = 'IPC controlled Motor of BS1, sample side',
                        abslimits = (-177.315, 142.685),
                        userlimits = (-177.002, 139.998),
                        bus = 'nokbus4',     # from ipcsms_*.res
                        addr = 0x68,     # from resources.inf
                        slope = 800.0,   # FULL steps per physical unit
                        speed = 5,
                        accel = 5,
                        confbyte = 32,
                        ramptype = 2,
                        microstep = 1,
                        refpos = 89.529,     # from ipcsms_*.res
                        zerosteps = int(660.44 * 800),   # offset * slope
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    bs1s_obs   = device('refsans.nok_support.NOKPosition',
                        description = 'Position sensing for BS1, sample side',
                        reference = 'nok_refc2',
                        measure = 'bs1s_poti',
                        poly = [40.36065, 999.452 / 1.919],  # off, mul * 1000 / sensitivity, higher orders...
                        serial = 7784,
                        length = 500.0,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    bs1s_poti  = device('refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Poti for BS1, sample side',
                        tacodevice = '//%s/test/wb_c/2_2' % nethost,
                        scale = 1,   # mounted from bottom
                        lowlevel = True,
                       ),
)
