description = 'Virtual SPODI instrument'

group = 'basic'

includes = [
    'system', 'sampletable', 'detector', 'slits', 'filter', 'mono', 'reactor'
]

devices = dict(
    wav = device('nicos.devices.generic.ManualMove',
        description = 'The incoming wavelength',
        default = 1.7,
        fmtstr = '%.2f',
        unit = 'AA',
        abslimits = (0.9, 2.5),
    ),
)
