description = "neutronguide, radialcollimator"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus1', 'nokbus2']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    nok4           = device('nicos_mlz.refsans.nok_support.DoubleMotorNOK',
                            description = 'NOK4',
                            nok_start = 1326.0,
                            nok_length = 1000.0,
                            nok_end = 2326.0,
                            nok_gap = 1.0,
                            inclinationlimits = (-10, 10),   # invented values, PLEASE CHECK!
                            motor_r = 'nok4r_axis',
                            motor_s = 'nok4s_axis',
                            nok_motor = [1477.0, 2177.0],
                            backlash = -2,   # is this configured somewhere?
                            precision = 0.05,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok4r_axis     = device('nicos.devices.generic.Axis',
                            description = 'Axis of NOK4, reactor side',
                            motor = 'nok4r_motor',
                            coder = 'nok4r_motor',
                            obs = ['nok4r_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

    nok4_srll = device('nicos.devices.taco.DigitalInput',
                       description = 'Device test/nok4/srll of Server ipcsmsserver nok4',
                       tacodevice = '//%s/test/nok4/srll' % nethost,
                       lowlevel = True,
                      ),

    nok4_srhl = device('nicos.devices.taco.DigitalInput',
                       description = 'Device test/nok4/srhl of Server ipcsmsserver nok4',
                       tacodevice = '//%s/test/nok4/srhl' % nethost,
                       lowlevel = True,
                      ),

    nok4_srref = device('nicos.devices.taco.DigitalInput',
                        description = 'Device test/nok4/srref of Server ipcsmsserver nok4',
                        tacodevice = '//%s/test/nok4/srref' % nethost,
                        lowlevel = True,
                       ),

    nok4_srrel = device('nicos.devices.taco.DigitalInput',
                        description = 'Device test/nok4/srrel of Server ipcsmsserver nok4',
                        tacodevice = '//%s/test/nok4/srrel' % nethost,
                        lowlevel = True,
                       ),

    nok4_srsll = device('nicos.devices.taco.DigitalInput',
                        description = 'Device test/nok4/srsll of Server ipcsmsserver nok4',
                        tacodevice = '//%s/test/nok4/srsll' % nethost,
                        lowlevel = True,
                       ),

    nok4_srshl = device('nicos.devices.taco.DigitalInput',
                        description = 'Device test/nok4/srshl of Server ipcsmsserver nok4',
                        tacodevice = '//%s/test/nok4/srshl' % nethost,
                        lowlevel = True,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok4r_motor    = device('nicos_mlz.refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK4, reactor side',
                            abslimits = (-20.477, 48.523),
                            userlimits = (-20.477, 48.523),
                            bus = 'nokbus1',     # from ipcsms_*.res
                            addr = 0x36,     # from resources.inf
                            slope = 2000.0,  # FULL steps per physical unit
                            speed = 10,
                            accel = 10,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = 20.2135,    # from ipcsms_*.res
                            zerosteps = int(229.977 * 2000),     # offset * slope
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok4r_obs      = device('nicos_mlz.refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK4, reactor side',
                            reference = 'nok_refa2',
                            measure = 'nok4r_poti',
                            poly = [36.179259, 1002.569 / 3.852],    # off, mul * 1000 / sensitivity, higher orders...
                            serial = 6509,
                            length = 250.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok4r_poti     = device('nicos_mlz.refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK4, reactor side',
                            tacodevice = '//%s/test/wb_a/2_0' % nethost,
                            scale = 1,   # mounted from bottom
                            lowlevel = True,
                           ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf
    nok4s_axis     = device('nicos.devices.generic.Axis',
                            description = 'Axis of NOK4, sample side',
                            motor = 'nok4s_motor',
                            coder = 'nok4s_motor',
                            obs = ['nok4s_obs'],
                            backlash = 0,
                            precision = 0.05,
                            unit = 'mm',
                            lowlevel = True,
                           ),

    nok4_ssll = device('nicos.devices.taco.DigitalInput',
                       description = 'Device test/nok4/ssll of Server ipcsmsserver nok4',
                       tacodevice = '//%s/test/nok4/ssll' % nethost,
                       lowlevel = True,
                      ),

    nok4_sshl = device('nicos.devices.taco.DigitalInput',
                       description = 'Device test/nok4/sshl of Server ipcsmsserver nok4',
                       tacodevice = '//%s/test/nok4/sshl' % nethost,
                       lowlevel = True,
                      ),

    nok4_ssref = device('nicos.devices.taco.DigitalInput',
                        description = 'Device test/nok4/ssref of Server ipcsmsserver nok4',
                        tacodevice = '//%s/test/nok4/ssref' % nethost,
                        lowlevel = True,
                       ),

    nok4_ssrel = device('nicos.devices.taco.DigitalInput',
                        description = 'Device test/nok4/ssrel of Server ipcsmsserver nok4',
                        tacodevice = '//%s/test/nok4/ssrel' % nethost,
                        lowlevel = True,
                       ),

    nok4_sssll = device('nicos.devices.taco.DigitalInput',
                        description = 'Device test/nok4/sssll of Server ipcsmsserver nok4',
                        tacodevice = '//%s/test/nok4/sssll' % nethost,
                        lowlevel = True,
                       ),

    nok4_ssshl = device('nicos.devices.taco.DigitalInput',
                        description = 'Device test/nok4/ssshl of Server ipcsmsserver nok4',
                        tacodevice = '//%s/test/nok4/ssshl' % nethost,
                        lowlevel = True,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok4s_motor    = device('nicos_mlz.refsans.nok_support.NOKMotorIPC',
                            description = 'IPC controlled Motor of NOK4, sample side',
                            abslimits = (-21.3025, 41.1975),
                            userlimits = (-21.3025, 41.197),
                            bus = 'nokbus2',     # from ipcsms_*.res
                            addr = 0x41,     # from resources.inf
                            slope = 2000.0,  # FULL steps per physical unit
                            speed = 10,
                            accel = 10,
                            confbyte = 48,
                            ramptype = 2,
                            microstep = 1,
                            refpos = 9.143,  # from ipcsms_*.res
                            zerosteps = int(240.803 * 2000),     # offset * slope
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok4s_obs      = device('nicos_mlz.refsans.nok_support.NOKPosition',
                            description = 'Position sensing for NOK4, sample side',
                            reference = 'nok_refa2',
                            measure = 'nok4s_poti',
                            poly = [4.822946, 998.362 / 3.856],  # off, mul * 1000 / sensitivity, higher orders...
                            serial = 6504,
                            length = 250.0,
                            lowlevel = True,
                           ),

# generated from global/inf/poti_tracing.inf
    nok4s_poti     = device('nicos_mlz.refsans.nok_support.NOKMonitoredVoltage',
                            description = 'Poti for NOK4, sample side',
                            tacodevice = '//%s/test/wb_a/2_1' % nethost,
                            scale = 1,   # mounted from bottom
                            lowlevel = True,
                           ),
)
