description = "disc3 height"

group = 'lowlevel'

instrument_values = configdata('instrument.values')
tango_base = instrument_values['tango_base']

devices = dict(
    disc3 = device('nicos.devices.tango.Motor',
        description = 'disc 3 Motor',
        tangodevice = tango_base + 'optic/disc34/disc3',
        abslimits = (-43, 48),
        refpos = -5,
    ),
)
