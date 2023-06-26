description = 'Virtual TOFTOF instrument setup'

group = 'basic'

includes = [
    'detector', 'chopper', 'vacuum', 'voltage', 'table', 'slit', 'collimator',
    'rc', 'reactor',
    'nl2a',
]

startupcode = '''
SetDetectors(det)
SetEnvironment(ReactorPower)
# AddEnvironment(chDS)
'''
