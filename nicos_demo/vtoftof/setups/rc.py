description = 'TOFTOF radial collimator'

group = 'optional'

devices = dict(
    rc = device('nicos.devices.generic.ManualSwitch',
        description = 'Radial collimator',
        states = ['on', 'off'],
        requires = {'level': 'admin'},
        pollinterval = 10,
        maxage = 12,
    ),
)
