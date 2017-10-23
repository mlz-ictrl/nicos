description = 'PGAA setup with Huber sample table'

group = 'basic'

includes = ['system',
            'reactor',
            'nl4b',
            'pressure',
            'sampletable',
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
        lowlevel = True,
    )
)
