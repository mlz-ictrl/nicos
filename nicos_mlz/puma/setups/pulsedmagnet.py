description = 'Pulsed magnet'

group = 'optional'

tango_host = 'tango://puma5.puma.frm2:10000/puma/'

devices = dict(
    B_pm = device('nicos.devices.tango.Sensor',
        description = 'Hall sensor',
        tangodevice = tango_host + 'magnet/field',
    ),
    B_current = device('nicos.devices.tango.PowerSupply',
        description = 'Current through magnet coils',
        tangodevice = tango_host + 'ps/current',
    ),
)
