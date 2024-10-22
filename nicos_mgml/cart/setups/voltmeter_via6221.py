description = 'Reading Keithley voltmeter'

group = 'optional'

tango_base = 'tango://localhost:10000/cart/'


devices = dict(

    controlk6221 = device('nicos.devices.entangle.StringIO',
        tangodevice = tango_base + 'k6221/io',
        loglevel = 'info',
        visibility = (),
    ),

    VoltageDet = device('nicos_mgml.devices.k2182.Voltmeter',
        description = 'Voltmeter',
        fmtstr = '%.8f',
        k6221 = 'controlk6221',
    ),

    VoltageDev = device('nicos_mgml.devices.k2182.VoltageDev',
        description = 'Temperature of thermocouple',
        fmtstr = '%.8f',
        k6221 = 'controlk6221',
        precision = 0.1,
        window = 10,
    ),
)
