description = 'REFSANS setup for julabo01 Presto A40'

group = 'optional'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base'] + 'refsans/julabo01/control'

devices = dict(
    julabo_temp = device('nicos.devices.tango.TemperatureController',
        description = 'julabo01 temperature',
        tangodevice = tango_base,
    ),
)
