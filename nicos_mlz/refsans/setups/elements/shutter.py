description = 'Instrument shutter device'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

tango_base = instrument_values['tango_base']
code_base = instrument_values['code_base']

devices = dict(
    shutter_motor = device('nicos.devices.tango.Motor',
        description = 'Instrument shutter linear motor',
        tangodevice = tango_base + 'shutter/shutter/motor',
        abslimits = (0, 55),
        precision = 0.5,
        lowlevel = True,
    ),
    shutter = device(code_base + 'shutter.Shutter',
        description = 'Instrument shutter',
        moveable = 'shutter_motor',
        precision = 0.5,
        mapping = {'closed': 7,
                   'open': 65,
                   'safe':0.275,
                   },
        fallback = 'offline',
    ),
)
