description = 'Reference readouts for NOK poti'

group = 'lowlevel'

instrument_values = configdata('instrument.values')
tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

devices = dict(
    nok_refa1 = device(code_base + 'nok_support.NOKMonitoredVoltage',
        description = 'Reference for shutter_gamma, nok2r, nok2s, nok3r, nok3s',
        tangodevice = tango_base + 'test/wb_a/1_6',
        reflimits = (17.0, 18.0, 19.8),
        scale = 2,
        lowlevel = True,
    ),
    nok_refa2 = device(code_base + 'nok_support.NOKMonitoredVoltage',
        description = 'Reference for b1r, b1s, nok4r, nok4s',
        tangodevice = tango_base + 'test/wb_a/2_6',
        reflimits = (17.0, 18.0, 19.8),
        scale = 2,
        lowlevel = True,
    ),
    nok_refb1 = device(code_base + 'nok_support.NOKMonitoredVoltage',
        description = 'Reference for nok5ar, nok5as, nok5br, nok5bs, zb0',
        tangodevice = tango_base + 'test/wb_b/1_6',
        reflimits = (17.0, 18.0, 19.8),
        scale = 2,
        lowlevel = True,
    ),
    nok_refb2 = device(code_base + 'nok_support.NOKMonitoredVoltage',
        description = 'Reference for nok6r, nok6s, zb1, zb2',
        tangodevice = tango_base + 'test/wb_b/2_6',
        reflimits = (17.0, 18.0, 19.8),
        scale = 2,
        lowlevel = True,
    ),
    nok_refc1 = device(code_base + 'nok_support.NOKMonitoredVoltage',
        description = 'Reference for nok7r, nok7s, nok8r, zb3r, zb3s',
        tangodevice = tango_base + 'test/wb_c/1_6',
        reflimits = (17.0, 18.0, 19.8),
        scale = 2,
        lowlevel = True,
    ),
    nok_refc2 = device(code_base + 'nok_support.NOKMonitoredVoltage',
        description = 'Reference for bs1r, bs1s, nok8s, nok9r, nok9s',
        tangodevice = tango_base + 'test/wb_c/2_6',
        reflimits = (17.0, 18.0, 19.8),
        scale = 2,
        lowlevel = True,
    ),
)
