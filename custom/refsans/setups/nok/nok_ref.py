description = 'Reference readouts for NOK poti'

group = 'lowlevel'

includes = []

devices = dict(
# generated from global/inf/poti_tracing.inf
    nok_refa1  = device('nicos_mlz.refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Reference for nok1, nok2r, nok2s, nok3r, nok3s',
                        tacodevice = 'test/wb_a/1_6',
                        reflimits = (17.0, 18.0, 19.8),  # min, warn, max
                        scale = 2,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    nok_refa2  = device('nicos_mlz.refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Reference for b1r, b1s, nok4r, nok4s',
                        tacodevice = 'test/wb_a/2_6',
                        reflimits = (17.0, 18.0, 19.8),  # min, warn, max
                        scale = 2,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    nok_refb1  = device('nicos_mlz.refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Reference for nok5ar, nok5as, nok5br, nok5bs, zb0',
                        tacodevice = 'test/wb_b/1_6',
                        reflimits = (17.0, 18.0, 19.8),  # min, warn, max
                        scale = 2,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    nok_refb2  = device('nicos_mlz.refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Reference for nok6r, nok6s, zb1, zb2',
                        tacodevice = 'test/wb_b/2_6',
                        reflimits = (17.0, 18.0, 19.8),  # min, warn, max
                        scale = 2,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    nok_refc1  = device('nicos_mlz.refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Reference for nok7r, nok7s, nok8r, zb3r, zb3s',
                        tacodevice = 'test/wb_c/1_6',
                        reflimits = (17.0, 18.0, 19.8),  # min, warn, max
                        scale = 2,
                        lowlevel = True,
                       ),

# generated from global/inf/poti_tracing.inf
    nok_refc2  = device('nicos_mlz.refsans.nok_support.NOKMonitoredVoltage',
                        description = 'Reference for bs1r, bs1s, nok8s, nok9r, nok9s',
                        tacodevice = 'test/wb_c/2_6',
                        reflimits = (17.0, 18.0, 19.8),  # min, warn, max
                        scale = 2,
                        lowlevel = True,
                       ),
)
