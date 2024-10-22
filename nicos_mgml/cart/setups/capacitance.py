description = 'Capacitance over AH capacitance bridge'

group = 'optional'

tango_base = 'tango://localhost:10000/cart/'


devices = dict(

    busah2500 = device('nicos.devices.entangle.StringIO',
        tangodevice = tango_base + 'ah2500a/io',
        loglevel = 'info',
        visibility = (),
        comtries = 5,
        comdelay = 2.0,
    ),

    Capacitance = device('nicos_mgml.devices.ahbridge.Capacitance',
        description = 'Capacitance bridge',
        fmtstr = '%.9f',
        ah2500 = 'busah2500',
    ),
)
