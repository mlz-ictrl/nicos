description = 'REFSANS setup for julabo01 Presto A40'

group = 'optional'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base'] + 'refsans/julabo01/'

devices = dict(
    julabo_temp = device('nicos.devices.tango.TemperatureController',
        description = 'Julabo01 temperature control',
        tangodevice = tango_base + 'control',
        fmtstr = '%.2f',
    ),
    julabo_int = device('nicos.devices.tango.Sensor',
        description = 'Julabo01 temperature bath',
        tangodevice = tango_base + 'intsensor',
        fmtstr = '%.2f',
    ),
    julabo_ext = device('nicos.devices.tango.Sensor',
        description = 'Julabo01 external sensor',
        tangodevice = tango_base + 'extsensor',
        fmtstr = '%.2f',
    ),
)
