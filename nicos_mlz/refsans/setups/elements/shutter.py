description = 'Instrument shutter device'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base']

devices = dict(
    shutter_m = device('nicos.devices.tango.Motor',
        description = 'Instrument shutter linear motor',
        tangodevice = tango_base + 'shutter/shutter/motor',
        abslimits = (0, 55),
        precision = 0.5,
        lowlevel = True,
    ),
    shutter = device('nicos_mlz.refsans.devices.shutter.Shutter',
        description = 'Instrument shutter',
        moveable = 'shutter_m',
        precision = 0.5,
        mapping = {'closed': 7,
                   'open': 65,
                   'safe':0.275,
                   },
        fallback = 'offline',
    ),
)
