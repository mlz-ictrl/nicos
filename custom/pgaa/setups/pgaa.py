description = 'PGAA setup'

group = 'basic'

sysconfig = dict(
    datasinks = ['sink']
)

includes = ['system',
            'reactor',
            'nl4b',
            'pressure',
            'sample',
            'pilz',
            'detector',
           ]

devices = dict(
    sink = device('pgaa.datasinks.PGAASink',
                  settypes = set(['scan']),
                  det1 = 'det',
                  det2 = 'detLEGe',
                  vac = 'chamber_pressure',
                  lowlevel = True,
                 ),
)
