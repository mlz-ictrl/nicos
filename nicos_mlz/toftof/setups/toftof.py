description = 'TOFTOF basic instrument setup'

group = 'basic'

includes = [
    'detector',
    'chopper',
    'vacuum',
    'voltage',
    'safety',
    'reactor',
    'guidehall',
    'nl2a',
    'table',
    'slit',
    'collimator',
    'rc',
    'samplememograph',
]

startupcode='''
SetDetectors(det)
'''
