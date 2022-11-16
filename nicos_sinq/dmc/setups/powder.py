description = 'DMC configuration for powder sample experiment'
group = 'basic'

devices = dict(
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
)
