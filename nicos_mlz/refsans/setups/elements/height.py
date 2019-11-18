description = 'Sample surface position measurement'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base'] + 'tristate.TriState'

devices = dict(
    height = device(code_base,
        description = 'Sample surface position.',
        unit = 'mm',
        port = 'height_port',
    ),
    height_port = device('nicos.devices.tango.Sensor',
        description = 'Sample surface position',
        tangodevice = tango_base + 'refsans/keyence/sensor',
        unit = 'mm',
        lowlevel = True,
    ),
)
