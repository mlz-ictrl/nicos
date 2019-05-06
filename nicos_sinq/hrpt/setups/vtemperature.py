description = 'For testing environment support and NeXus writing'

group = 'optional'


devices = dict(
    tt = device('nicos.devices.generic.VirtualTemperature',
        description = 'Temperature of the World',
        abslimits = (4, 600),
        warnlimits = (6, 600),
        precision = .2,
        jitter = 1.3,
        speed = 6,
        unit = 'K',
    ),
)