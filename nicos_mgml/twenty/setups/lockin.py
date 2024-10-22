description = 'Reading Keithley multimeter as a counter'

group = 'optional'

tango_base = 'tango://localhost:10000/20t/'


devices = dict(

    bussr830 = device('nicos.devices.entangle.StringIO',
        tangodevice = tango_base + 'sr830/io',
        loglevel = 'info',
        visibility = (),
    ),

    Lockin = device('nicos_mgml.devices.lockin.Lockinmeter',
        description = 'Lock-In amplifier',
        fmtstr = '%.8f',
        sr830 = 'bussr830',
    ),
)
