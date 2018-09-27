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
    'samplechanger',
    'pilz',
    'detector',
    'collimation',
]

devices = dict(
    sink = device('nicos_mlz.pgaa.devices.PGAASink',
        settypes = set(['scan']),
        det1 = '_60p',
        det2 = 'LEGe',
        vac = 'chamber_pressure',
    ),
)
