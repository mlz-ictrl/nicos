description = 'Capacitance over AH capacitance bridge'

group = 'optional'

tango_base = 'tango://localhost:10000/20t/'


devices = dict(

    busah2550 = device('nicos.devices.entangle.StringIO',
        tangodevice = tango_base + 'ah2550a/io',
        loglevel = 'info',
        visibility = (),
    ),

    Capacitance = device('nicos_mgml.devices.ahbridge.Capacitance',
        description = 'Capacitance bridge',
        fmtstr = '%.9f',
        ah2500 = 'busah2550',
    ),
)
