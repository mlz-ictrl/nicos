description = 'Reading Keithley voltmeter'

group = 'optional'

tango_base = 'tango://localhost:10000/cart/'


devices = dict(

    controlk2182 = device('nicos.devices.entangle.StringIO',
        tangodevice = tango_base + 'k2182/io',
        loglevel = 'info',
        visibility = (),
    ),

    VoltageDirectDev = device('nicos_mgml.devices.k2182.VoltageDev',
        description = 'Seebeck voltage',
        fmtstr = '%.8f',
        k2182 = 'controlk2182',
        precision = 0.1,
        window = 20,
    ),
)
