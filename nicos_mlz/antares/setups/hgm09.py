description = 'HGM09 Hand Gauss Meter'

group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    hgm09 = device('nicos.devices.entangle.Sensor',
        description = 'HGM09 Hand Gauss Meter',
        tangodevice = tango_base + 'hgm09/sensor',
    ),
)
