description = 'PGAA setup with sample changer'

group = 'basic'

sysconfig = dict(
    datasinks = ['sink']
)

includes = [
    'system',
    'reactor',
    'nl4b',
    'pressure',
    'sample',
    'pilz',
    'detector',
    'collimation',
]

devices = dict(
    sink = device('nicos_mlz.pgaa.devices.PGAASink',
        settypes = set(['scan']),
        det1 = 'det',
        det2 = 'detLEGe',
        vac = 'chamber_pressure',
        lowlevel = True,
    ),
)
