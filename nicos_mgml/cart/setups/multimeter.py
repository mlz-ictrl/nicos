description = 'Reading Keysight multimeter'

group = 'optional'

tango_base = 'tango://localhost:10000/cart/'


devices = dict(

    busk34450 = device('nicos.devices.entangle.StringIO',
        tangodevice = tango_base + 'edu34450a/io',
        loglevel = 'info',
        visibility = (),
    ),

    Multimeter = device('nicos_mgml.devices.k34450.Multimeter',
        description = 'Keysight k23350 multimeter',
        fmtstr = '%.6f',
        k34450 = 'busk34450',
    ),
)
