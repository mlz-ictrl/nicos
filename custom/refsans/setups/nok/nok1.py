description = "neutronguide, leadblock"

group = 'lowlevel'

includes = ['nok_ref', 'nokbus1']

nethost = 'refsanssrv.refsans.frm2'

devices = dict(
    nok1       = device('refsans.nok_support.SingleMotorNOK',
                        description = 'NOK1',
                        motor = 'nok1_motor',
                        coder = 'nok1_motor',
                        obs = ['nok1_obs'],
                        nok_start = 198.0,
                        nok_length = 90.0,
                        nok_end = 288.0,
                        nok_gap = 1.0,
                        backlash = -2,   # is this configured somewhere?
                        precision = 0.05,
                       ),
    nok1_srrel = device('nicos.devices.taco.DigitalInput',
                        description = 'Device test/nok1/srrel of Server ipcsmsserver nok1',
                        tacodevice = '//%s/test/nok1/srrel' % nethost,
                        lowlevel = True,
                       ),

    nok1_srll = device('nicos.devices.taco.DigitalInput',
                       description = 'Device test/nok1/srll of Server ipcsmsserver nok1',
                       tacodevice = '//%s/test/nok1/srll' % nethost,
                       lowlevel = True,
                      ),

    nok1_srhl = device('nicos.devices.taco.DigitalInput',
                       description = 'Device test/nok1/srhl of Server ipcsmsserver nok1',
                       tacodevice = '//%s/test/nok1/srhl' % nethost,
                       lowlevel = True,
                      ),

    nok1_srref = device('nicos.devices.taco.DigitalInput',
                        description = 'Device test/nok1/srref of Server ipcsmsserver nok1',
                        tacodevice = '//%s/test/nok1/srref' % nethost,
                        lowlevel = True,
                       ),

    nok1_srsll = device('nicos.devices.taco.DigitalInput',
                        description = 'Device test/nok1/srsll of Server ipcsmsserver nok1',
                        tacodevice = '//%s/test/nok1/srsll' % nethost,
                        lowlevel = True,
                       ),

    nok1_srshl = device('nicos.devices.taco.DigitalInput',
                        description = 'Device test/nok1/srshl of Server ipcsmsserver nok1',
                        tacodevice = '//%s/test/nok1/srshl' % nethost,
                        lowlevel = True,
                       ),

# generated from global/inf/resources.inf, geometrie.inf, optic.inf and taco *.res files
    nok1_motor = device('refsans.nok_support.NOKMotorIPC',
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
    nok1_obs   = device('refsans.nok_support.NOKPosition',
                        description = 'Position sensing for NOK1',
                        reference = 'nok_refa1',
                        measure = 'nok1_poti',
                        poly = [-13.748035, 996.393 / 3.856],    # off, mul * 1000 / sensitivity, higher orders...
                        serial = 6505,
                        length = 250.0,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    nok1_poti  = device('refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Poti for NOK1',
                        tacodevice = '//%s/test/wb_a/1_0' % nethost,
                        scale = 1,   # mounted from bottom
                        lowlevel = True,
                       ),
)
