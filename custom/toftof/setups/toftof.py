description = 'TOFTOF basic instrument setup'

group = 'basic'

includes = [
    'detector',
    'chopper',
    'vacuum',
    'voltage',
    'safety',
    'reactor',
    'table',
    'slit',
    'collimator',
    'rc',
    'samplememograph',
]

startupcode='''
SetDetectors(det)
'''
