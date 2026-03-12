description = 'DMC configuration for powder sample experiment'

group = 'basic'

includes = [
    'detector',
    'monochromator',
    'gaspump',
]

devices = dict(
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
)
