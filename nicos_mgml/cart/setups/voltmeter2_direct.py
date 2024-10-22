description = 'Reading Keithley voltmeter'

group = 'optional'

tango_base = 'tango://localhost:10000/cart/'


devices = dict(

    controlk2182v2 = device('nicos.devices.entangle.StringIO',
        tangodevice = tango_base + 'k2182v2/io',
        loglevel = 'info',
        visibility = (),
    ),

    VoltageDev = device('nicos_mgml.devices.k2182.VoltageDev',
        description = 'Temperature of thermocouple',
        fmtstr = '%.8f',
        k2182 = 'controlk2182v2',
        precision = 0.1,
        window = 20,
    ),
)
