description = 'Virtual TOFTOF instrument setup'

group = 'basic'

includes = [
    'detector', 'chopper', 'vacuum', 'voltage', 'table', 'slit', 'collimator',
    'rc', 'reactor',
]

startupcode = '''
SetDetectors(det)
SetEnvironment(ReactorPower)
# AddEnvironment(chDS)
'''
