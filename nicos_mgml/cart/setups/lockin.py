description = 'Reading Lock-in at GPIB 8'

group = 'optional'

tango_base = 'tango://localhost:10000/cart/'


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
