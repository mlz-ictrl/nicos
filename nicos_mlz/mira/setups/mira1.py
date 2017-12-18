description = 'MIRA 1 measurements'
group = 'basic'

includes = ['base', 'mono1', 'sample', 'detector', 'mslit1']

devices = dict(
    Sample = device('nicos.devices.tas.TASSample',
        description = 'sample object',
    ),
)
