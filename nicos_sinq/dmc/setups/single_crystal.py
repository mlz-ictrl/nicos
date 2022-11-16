description = 'DMC configuration for single crystal experiment'
group = 'basic'

devices = dict(
    sample = device('nicos_sinq.devices.sample.CrystalSample',
        description = 'The currently used sample',
        a = 9.8412,
    ),
)
