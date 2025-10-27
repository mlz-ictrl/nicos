description = 'Virtual SPODI instrument'

group = 'basic'

includes = [
    'system', 'sampletable', 'detector', 'slits', 'filter', 'mono', 'reactor',
    'nguide',
]

devices = dict(
    wav = device('nicos.devices.generic.CrystalMonochromator',
        description = 'The incoming wavelength',
        unit = 'A',
        theta = 'omgm',
        twotheta = 'tthm',
        material = 'Ge',
        reflection = (5, 5, 1),
        fmtstr = '%.3f',
        abslimits = (0.5, 3.0),
    ),
)
