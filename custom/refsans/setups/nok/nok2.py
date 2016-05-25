description = "neutronguid"

group = 'optional'

includes = ['nok_ref', 'nokbus1']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    nok2           = device('refsans.nok_support.DoubleMotorNOK',
                            description = 'NOK2',
                            nok_start = 334.0,
                            nok_length = 300.0,
                            nok_end = 634.0,
                            nok_gap = 1.0,
                            inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                            motor_r = 'nok2r_axis',
                            motor_s = 'nok2s_axis',
                            nok_motor = [408.5, 585.0],
                            backlash = -2,   # is this configured somewhere?
                            precision = 0.05,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok2r_axis     = device('devices.generic.Axis',
                            description = 'Axis of NOK2, reactor side',
                            motor = 'nok2r_motor',
                            coder = 'nok2r_motor',
                            obs = ['nok2r_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok2r_motor    = device('refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK2, reactor side',
                            abslimits = (-254.36, 56.14),
                            userlimits = (-22.36, 10.88),
                            bus = 'nokbus1',     # from ipcsms_*.res
                            addr = 0x32,     # from resources.inf
                            slope = 2000.0,  # FULL steps per physical unit
                            speed = 10,
                            accel = 10,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = -4.42,  # from ipcsms_*.res
                            zerosteps = int(254.36 * 2000),  # offset * slope
                            lowlevel = True,
                           ),

    nok2_sshl = device('devices.taco.DigitalInput',
                       description = 'high limit switch',
                       tacodevice = '//%s/test/nok2/sshl' % nethost,
                       #lowlevel = True,
                      ),

    nok2_ssll = device('devices.taco.DigitalInput',
                       description = 'low limit switch',
                       tacodevice = '//%s/test/nok2/ssll' % nethost,
                       #lowlevel = True,
                      ),

    nok2_ssref = device('devices.taco.DigitalInput',
                        description = 'Device test/nok2/ssref of Server ipcsmsserver nok2',
                        tacodevice = '//%s/test/nok2/ssref' % nethost,
                        #lowlevel = True,
                       ),

    nok2_ssrel = device('devices.taco.DigitalInput',
                        description = 'Device test/nok2/ssrel of Server ipcsmsserver nok2',
                        tacodevice = '//%s/test/nok2/ssrel' % nethost,
                        #lowlevel = True,
                       ),

    nok2_sssll = device('devices.taco.DigitalInput',
                        description = 'Device test/nok2/sssll of Server ipcsmsserver nok2',
                        tacodevice = '//%s/test/nok2/sssll' % nethost,
                        #lowlevel = True,
                       ),

    nok2_ssshl = device('devices.taco.DigitalInput',
                        description = 'Device test/nok2/ssshl of Server ipcsmsserver nok2',
                        tacodevice = '//%s/test/nok2/ssshl' % nethost,
                        #lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    nok2r_obs      = device('refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK2, reactor side',
                            reference = 'nok_refa1',
                            measure = 'nok2r_poti',
                            poly = [9.169441, 996.418 / 3.858],  # off, mul * 1000 / sensitivity, higher orders...
                            serial = 6510,
                            length = 250.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok2r_poti     = device('refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK2, reactor side',
                            tacodevice = '//%s/test/wb_a/1_1' % nethost,
                            scale = 1,   # mounted from bottom
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok2s_axis     = device('devices.generic.Axis',
                            description = 'Axis of NOK2, sample side',
                            motor = 'nok2s_motor',
                            coder = 'nok2s_motor',
                            obs = ['nok2s_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok2s_motor    = device('refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK2, sample side',
                            abslimits = (-268.11, 231.889),
                            userlimits = (-21.61, 6.885),
                            bus = 'nokbus1',     # from ipcsms_*.res
                            addr = 0x33,     # from resources.inf
                            slope = 2000.0,  # FULL steps per physical unit
                            speed = 10,
                            accel = 10,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = -18.19,     # from ipcsms_*.res
                            zerosteps = int(268.11 * 2000),  # offset * slope
                            lowlevel = True,
                           ),

    nok2_srll = device('devices.taco.DigitalInput',
                       description = 'Device test/nok2/srll of Server ipcsmsserver nok2',
                       tacodevice = '//%s/test/nok2/srll' % nethost,
                       #lowlevel = True,
                      ),

    nok2_srhl = device('devices.taco.DigitalInput',
                       description = 'Device test/nok2/srhl of Server ipcsmsserver nok2',
                       tacodevice = '//%s/test/nok2/srhl' % nethost,
                       lowlevel = False,
                      ),

    nok2_srref = device('devices.taco.DigitalInput',
                        description = 'Device test/nok2/srref of Server ipcsmsserver nok2',
                        tacodevice = '//%s/test/nok2/srref' % nethost,
                        #lowlevel = True,
                       ),

    nok2_srrel = device('devices.taco.DigitalInput',
                        description = 'Device test/nok2/srrel of Server ipcsmsserver nok2',
                        tacodevice = '//%s/test/nok2/srrel' % nethost,
                        #lowlevel = True,
                       ),

    nok2_srsll = device('devices.taco.DigitalInput',
                        description = 'Device test/nok2/srsll of Server ipcsmsserver nok2',
                        tacodevice = '//%s/test/nok2/srsll' % nethost,
                        #lowlevel = True,
                       ),

    nok2_srshl = device('devices.taco.DigitalInput',
                        description = 'Device test/nok2/srshl of Server ipcsmsserver nok2',
                        tacodevice = '//%s/test/nok2/srshl' % nethost,
                        #lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    nok2s_obs      = device('refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK2, sample side',
                            reference = 'nok_refa1',
                            measure = 'nok2s_poti',
                            poly = [-22.686241, 1003.096 / 3.846],   # off, mul * 1000 / sensitivity, higher orders...
                            serial = 6512,
                            length = 250.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok2s_poti     = device('refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK2, sample side',
                            tacodevice = '//%s/test/wb_a/1_2' % nethost,
                            scale = 1,   # mounted from bottom
                            lowlevel = True,
                           ),
)
