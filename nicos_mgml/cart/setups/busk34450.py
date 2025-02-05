description = 'Reading Keysight multimeter'

group = 'optional'

tango_base = 'tango://localhost:10000/cart/'

devices = dict(
    busk34450 = device('nicos.devices.entangle.StringIO',
        tangodevice = tango_base + 'edu34450a/io',
        loglevel = 'info',
        visibility = (),
    ),
)
