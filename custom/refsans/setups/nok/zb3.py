description = "DoubleSlit [slit k1] between nok6 and nok7"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus3']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
# masks:
# 12.01.2010 10:34:54 (k1)
# 12.06.2009 16:22:34 centertest2 (slit)
    zb3        = device('refsans.nok_support.DoubleMotorNOK',
                        description = 'ZB3',
                        nok_start = 8837.5,
                        nok_length = 13.0,
                        nok_end = 8850.5,
                        nok_gap = 1.0,
                        inclinationlimits = (-1000, 1000),   # invented values, PLEASE CHECK!
                        masks = dict(
                                     k1   = [-110.0, 0.0, -2.64, 0.0],
                                     slit = [0.0, 0.0, -2.63, -0.57],
                                    ),
                        motor_r = 'zb3r_axis',
                        motor_s = 'zb3s_axis',
                        nok_motor = [8843.5, 8850.5],
                        backlash = -2,   # is this configured somewhere?
                        precision = 0.05,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    zb3r_axis  = device('devices.generic.Axis',
                        description = 'Axis of ZB3, reactor side',
                        motor = 'zb3r_motor',
                        coder = 'zb3r_motor',
                        obs = ['zb3r_obs'],
                        backlash = 0,
                        precision = 0.05,
                        unit = 'mm',
                        lowlevel = True,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    zb3r_motor = device('refsans.nok_support.NOKMotorIPC',
                        description = 'IPC controlled Motor of ZB3, reactor side',
                        abslimits = (-677.125, 99.125),
                        userlimits = (-221.0, 95.0),
                        bus = 'nokbus3',     # from ipcsms_*.res
                        addr = 0x57,     # from resources.inf
                        slope = 800.0,   # FULL steps per physical unit
                        speed = 10,
                        accel = 10,
                        confbyte = 32,
                        ramptype = 2,
                        microstep = 1,
                        refpos = 105.837,    # from ipcsms_*.res
                        zerosteps = int(677.125 * 800),  # offset * slope
                        lowlevel = True,
                       ),

    zb3_ssshl = device('devices.taco.DigitalInput',
                       description = 'Device test/zb3/ssshl of Server ipcsmsserver zb3',
                       tacodevice = '//%s/test/zb3/ssshl' % nethost,
                       lowlevel = True,
                      ),

    zb3_sssll = device('devices.taco.DigitalInput',
                       description = 'Device test/zb3/sssll of Server ipcsmsserver zb3',
                       tacodevice = '//%s/test/zb3/sssll' % nethost,
                       lowlevel = True,
                      ),

    zb3_ssrel = device('devices.taco.DigitalInput',
                       description = 'Device test/zb3/ssrel of Server ipcsmsserver zb3',
                       tacodevice = '//%s/test/zb3/ssrel' % nethost,
                       lowlevel = True,
                      ),

    zb3_ssref = device('devices.taco.DigitalInput',
                       description = 'Device test/zb3/ssref of Server ipcsmsserver zb3',
                       tacodevice = '//%s/test/zb3/ssref' % nethost,
                       lowlevel = True,
                      ),

    zb3_sshl = device('devices.taco.DigitalInput',
                      description = 'Device test/zb3/sshl of Server ipcsmsserver zb3',
                      tacodevice = '//%s/test/zb3/sshl' % nethost,
                      lowlevel = True,
                     ),

    zb3_ssll = device('devices.taco.DigitalInput',
                      description = 'Device test/zb3/ssll of Server ipcsmsserver zb3',
                      tacodevice = '//%s/test/zb3/ssll' % nethost,
                      lowlevel = True,
                     ),

# generated from global/inf/poti_tracing.inf
    zb3r_obs   = device('refsans.nok_support.NOKPosition',
                        description = 'Position sensing for ZB3, reactor side',
                        reference = 'nok_refc1',
                        measure = 'zb3r_poti',
                        poly = [-140.539293, 1004.824 / 1.92],   # off, mul * 1000 / sensitivity, higher orders...
                        serial = 7778,
                        length = 500.0,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    zb3r_poti  = device('refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Poti for ZB3, reactor side',
                        tacodevice = '//%s/test/wb_c/1_2' % nethost,
                        scale = -1,  # mounted from top
                        lowlevel = True,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    zb3s_axis  = device('devices.generic.Axis',
                        description = 'Axis of ZB3, sample side',
                        motor = 'zb3s_motor',
                        coder = 'zb3s_motor',
                        obs = ['zb3s_obs'],
                        backlash = 0,
                        precision = 0.05,
                        unit = 'mm',
                        lowlevel = True,
                       ),

    zb3_srshl = device('devices.taco.DigitalInput',
                       description = 'Device test/zb3/srshl of Server ipcsmsserver zb3',
                       tacodevice = '//%s/test/zb3/srshl' % nethost,
                       lowlevel = True,
                      ),

    zb3_srsll = device('devices.taco.DigitalInput',
                       description = 'Device test/zb3/srsll of Server ipcsmsserver zb3',
                       tacodevice = '//%s/test/zb3/srsll' % nethost,
                       lowlevel = True,
                      ),

    zb3_srrel = device('devices.taco.DigitalInput',
                       description = 'Device test/zb3/srrel of Server ipcsmsserver zb3',
                       tacodevice = '//%s/test/zb3/srrel' % nethost,
                       lowlevel = True,
                      ),

    zb3_srref = device('devices.taco.DigitalInput',
                       description = 'Device test/zb3/srref of Server ipcsmsserver zb3',
                       tacodevice = '//%s/test/zb3/srref' % nethost,
                       lowlevel = True,
                      ),

    zb3_srhl = device('devices.taco.DigitalInput',
                      description = 'Device test/zb3/srhl of Server ipcsmsserver zb3',
                      tacodevice = '//%s/test/zb3/srhl' % nethost,
                      lowlevel = True,
                     ),

    zb3_srll = device('devices.taco.DigitalInput',
                      description = 'Device test/zb3/srll of Server ipcsmsserver zb3',
                      tacodevice = '//%s/test/zb3/srll' % nethost,
                      lowlevel = True,
                     ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    zb3s_motor = device('refsans.nok_support.NOKMotorIPC',
                        description = 'IPC controlled Motor of ZB3, sample side',
                        abslimits = (-150.8125, 113.5625),
                        userlimits = (-106.0, 113.562),
                        bus = 'nokbus3',     # from ipcsms_*.res
                        addr = 0x58,     # from resources.inf
                        slope = 800.0,   # FULL steps per physical unit
                        speed = 10,
                        accel = 10,
                        confbyte = 32,
                        ramptype = 2,
                        microstep = 1,
                        refpos = 72.774,     # from ipcsms_*.res
                        zerosteps = int(644.562 * 800),  # offset * slope
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    zb3s_obs   = device('refsans.nok_support.NOKPosition',
                        description = 'Position sensing for ZB3, sample side',
                        reference = 'nok_refc1',
                        measure = 'zb3s_poti',
                        poly = [118.68, 1000. / 1.921],    # off, mul * 1000 / sensitivity, higher orders...
                        serial = 7781,
                        length = 500.0,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    zb3s_poti  = device('refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Poti for ZB3, sample side',
                        tacodevice = '//%s/test/wb_c/1_3' % nethost,
                        scale = 1,   # mounted from bottom
                        lowlevel = True,
                       ),
)
