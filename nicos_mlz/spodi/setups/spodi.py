description = 'SPODI setup'

group = 'basic'

includes = [
    'system', 'sampletable', 'detector', 'nguide', 'slits', 'filter',
    'mono', 'reactor'
]

# CHIT=(-180,180)

devices = dict(
    wav = device('nicos.devices.generic.CrystalMonochromator',
        description = 'The incoming wavelength',
        unit = 'A',
        theta = 'omgm',
        twotheta = 'tthm',
        material = 'Ge',
        reflection = (5, 5, 1),
        fmtstr = '%.3f',
        # abslimits = (1, 2.6),
    ),
)
