description = 'Reading Keithley voltmeter'

group = 'optional'

tango_base = 'tango://localhost:10000/dr/'


devices = dict(

    controlk6221Seebeck = device('nicos.devices.entangle.StringIO',
        tangodevice = tango_base + 'k6221/io',
        loglevel = 'info',
        visibility = (),
    ),

    VoltageDetSeebeck = device('nicos_mgml.devices.k2182.Voltmeter',
        description = 'Voltmeter for Seebeck as detector',
        fmtstr = '%.8f',
        k6221 = 'controlk6221Seebeck',
    ),

    VoltageDevSeebeck = device('nicos_mgml.devices.k2182.VoltageDev',
        description = 'Seebeck voltage',
        fmtstr = '%.8f',
        k6221 = 'controlk6221Seebeck',
        precision = 0.1,
        window = 10,
    ),
)
