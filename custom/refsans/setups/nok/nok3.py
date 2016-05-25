description = "neutronguid, radialcollimator"

group = 'optional'

includes = ['nok_ref', 'nokbus1']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    nok3           = device('refsans.nok_support.DoubleMotorNOK',
                            description = 'NOK3',
                            nok_start = 680.0,
                            nok_length = 600.0,
                            nok_end = 1280.0,
                            nok_gap = 1.0,
                            inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                            motor_r = 'nok3r_axis',
                            motor_s = 'nok3s_axis',
                            nok_motor = [831.0, 1131.0],
                            backlash = -2,   # is this configured somewhere?
                            precision = 0.05,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok3r_axis     = device('devices.generic.Axis',
                            description = 'Axis of NOK3, reactor side',
                            motor = 'nok3r_motor',
                            coder = 'nok3r_motor',
                            obs = ['nok3r_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

    nok3_srref = device('devices.taco.DigitalInput',
                        description = 'Device test/nok3/srref of Server ipcsmsserver nok3',
                        tacodevice = '//%s/test/nok3/srref' % nethost,
                       ),

    nok3_srrel = device('devices.taco.DigitalInput',
                        description = 'Device test/nok3/srrel of Server ipcsmsserver nok3',
                        tacodevice = '//%s/test/nok3/srrel' % nethost,
                       ),

    nok3_srsll = device('devices.taco.DigitalInput',
                        description = 'Device test/nok3/srsll of Server ipcsmsserver nok3',
                        tacodevice = '//%s/test/nok3/srsll' % nethost,
                       ),

    nok3_srshl = device('devices.taco.DigitalInput',
                        description = 'Device test/nok3/srshl of Server ipcsmsserver nok3',
                        tacodevice = '//%s/test/nok3/srshl' % nethost,
                       ),

    nok3_srll = device('devices.taco.DigitalInput',
                       description = 'Device test/nok3/srll of Server ipcsmsserver nok3',
                       tacodevice = '//%s/test/nok3/srll' % nethost,
                      ),

    nok3_srhl = device('devices.taco.DigitalInput',
                       description = 'Device test/nok3/srhl of Server ipcsmsserver nok3',
                       tacodevice = '//%s/test/nok3/srhl' % nethost,
                      ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok3r_motor    = device('refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK3, reactor side',
                            abslimits = (-21.967, 47.783),
                            userlimits = (-21.967, 47.782),
                            bus = 'nokbus1',     # from ipcsms_*.res
                            addr = 0x34,     # from resources.inf
                            slope = 2000.0,  # FULL steps per physical unit
                            speed = 10,
                            accel = 10,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = 20.6225,    # from ipcsms_*.res
                            zerosteps = int(229.467 * 2000),     # offset * slope
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok3r_obs      = device('refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK3, reactor side',
                            reference = 'nok_refa1',
                            measure = 'nok3r_poti',
                            poly = [21.830175, 997.962 / 3.846],     # off, mul * 1000 / sensitivity, higher orders...
                            serial = 6507,
                            length = 250.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok3r_poti     = device('refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK3, reactor side',
                            tacodevice = '//%s/test/wb_a/1_3' % nethost,
                            scale = 1,   # mounted from bottom
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok3s_axis     = device('devices.generic.Axis',
                            description = 'Axis of NOK3, sample side',
                            motor = 'nok3s_motor',
                            coder = 'nok3s_motor',
                            obs = ['nok3s_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

    nok3_ssll = device('devices.taco.DigitalInput',
                       description = 'Device test/nok3/ssll of Server ipcsmsserver nok3',
                       tacodevice = '//%s/test/nok3/ssll' % nethost,
                      ),

    nok3_sshl = device('devices.taco.DigitalInput',
                       description = 'Device test/nok3/sshl of Server ipcsmsserver nok3',
                       tacodevice = '//%s/test/nok3/sshl' % nethost,
                      ),

    nok3_ssref = device('devices.taco.DigitalInput',
                        description = 'Device test/nok3/ssref of Server ipcsmsserver nok3',
                        tacodevice = '//%s/test/nok3/ssref' % nethost,
                       ),

    nok3_ssrel = device('devices.taco.DigitalInput',
                        description = 'Device test/nok3/ssrel of Server ipcsmsserver nok3',
                        tacodevice = '//%s/test/nok3/ssrel' % nethost,
                       ),

    nok3_sssll = device('devices.taco.DigitalInput',
                        description = 'Device test/nok3/sssll of Server ipcsmsserver nok3',
                        tacodevice = '//%s/test/nok3/sssll' % nethost,
                       ),

    nok3_ssshl = device('devices.taco.DigitalInput',
                        description = 'Device test/nok3/ssshl of Server ipcsmsserver nok3',
                        tacodevice = '//%s/test/nok3/ssshl' % nethost,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok3s_motor    = device('refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK3, sample side',
                            abslimits = (-20.9435, 40.8065),
                            userlimits = (-20.944, 40.8055),
                            bus = 'nokbus1',     # from ipcsms_*.res
                            addr = 0x35,     # from resources.inf
                            slope = 2000.0,  # FULL steps per physical unit
                            speed = 10,
                            accel = 10,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = 9.444,  # from ipcsms_*.res
                            zerosteps = int(240.694 * 2000),     # offset * slope
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok3s_obs      = device('refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK3, sample side',
                            reference = 'nok_refa1',
                            measure = 'nok3s_poti',
                            poly = [10.409698, 1003.196 / 3.854],    # off, mul * 1000 / sensitivity, higher orders...
                            serial = 6506,
                            length = 250.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok3s_poti     = device('refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK3, sample side',
                            tacodevice = '//%s/test/wb_a/1_4' % nethost,
                            scale = 1,   # mounted from bottom
                            lowlevel = True,
                           ),
)
