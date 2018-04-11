description = 'Instrument shutter device'

group = 'lowlevel'

devices = dict(
    shutter_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Instrument shutter linear motor',
        abslimits = (0, 55),
        precision = 0.5,
        lowlevel = True,
        speed = 150.,
        unit = 'mm',
    ),
    shutter = device('nicos.devices.generic.Switcher',
        description = 'Instrument shutter',
        moveable = 'shutter_m',
        precision = 0.5,
        mapping = {'closed': 0,
                   'open': 55},
        fallback = 'offline',
    ),
)
