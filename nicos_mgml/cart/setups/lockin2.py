description = 'Reading Lock-in at GPIB 9'

group = 'optional'

tango_base = 'tango://localhost:10000/cart/'


devices = dict(

    bussr830_2 = device('nicos.devices.entangle.StringIO',
        tangodevice = tango_base + 'sr830_2/io',
        loglevel = 'info',
        visibility = (),
    ),

    Lockin2 = device('nicos_mgml.devices.lockin.Lockinmeter',
        description = 'Lock-In amplifier',
        fmtstr = '%.8f',
        sr830 = 'bussr830_2',
    ),
)
