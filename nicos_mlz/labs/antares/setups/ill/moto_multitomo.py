description = 'Multitomo setup for MoTo'

group = 'optional'

excludes = []

tango_host = 'phytron2.antareslab'

tango_base = f'tango://{tango_host}:10000/box/'

devices = dict(
    sry0 = device('nicos.devices.entangle.Motor',
        speed = 2.5,
        unit = 'deg',
        description = 'Rotation of sample 0',
        tangodevice = tango_base + 'phytron4/mot',
        abslimits = (-999, 999),
        maxage = 5,
        pollinterval = 3,
        precision = 0.01,
    ),
    sry1 = device('nicos.devices.entangle.Motor',
        speed = 2.5,
        unit = 'deg',
        description = 'Rotation of sample 1',
        tangodevice = tango_base + 'phytron5/mot',
        abslimits = (-999, 999),
        maxage = 5,
        pollinterval = 3,
        precision = 0.01,
    ),
    sry2 = device('nicos.devices.entangle.Motor',
        speed = 2.5,
        unit = 'deg',
        description = 'Rotation of sample 2',
        tangodevice = tango_base + 'phytron8/mot',
        abslimits = (-999, 999),
        maxage = 5,
        pollinterval = 3,
        precision = 0.01,
    ),
    sry3 = device('nicos.devices.entangle.Motor',
        speed = 2.5,
        unit = 'deg',
        description = 'Rotation of sample 3',
        tangodevice = tango_base + 'phytron7/mot',
        abslimits = (-999, 999),
        maxage = 5,
        pollinterval = 3,
        precision = 0.01,
    ),
)
