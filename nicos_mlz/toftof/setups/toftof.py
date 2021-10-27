description = 'TOFTOF basic instrument setup'

group = 'basic'

includes = [
    'detector',
    'chopper',
    'vacuum',
    'voltage',
    'safety',
    'reactor',
    'nl2a',
    'table',
    'slit',
    'collimator',
    'rc',
    'samplememograph',
    'chiller',
]

startupcode = '''
SetDetectors(det)
'''
