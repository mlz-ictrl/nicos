description = 'Reading Keysight voltmeter'

group = 'optional'

tango_base = 'tango://localhost:10000/cart/'


devices = dict(

    controlk34420 = device('nicos.devices.entangle.StringIO',
        tangodevice = tango_base + 'k34420/io',
        loglevel = 'info',
        visibility = (),
    ),

    VoltageSeebeckDev = device('nicos_mgml.devices.k34420.VoltageDev',
        description = 'Seebeck voltage',
        fmtstr = '%.8f',
        k34420 = 'controlk34420',
        precision = 0.1,
        window = 20,
    ),
)
