description = "disc4 height"

group = 'lowlevel'

instrument_values = configdata('instrument.values')
tango_base = instrument_values['tango_base']

devices = dict(
    disc4 = device('nicos.devices.tango.Motor',
        description = 'disc 4 Motor',
        tangodevice = tango_base + 'optic/disc34/disc4',
        abslimits = (-30, 46),
        lowlevel = False,
    ),
)
