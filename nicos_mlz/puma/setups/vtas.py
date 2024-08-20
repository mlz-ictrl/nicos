description = 'PUMA triple-axis setup with McStas simulated detector'

includes = ['pumabase', 'seccoll', 'collimation', 'ios', 'hv', 'notifiers',
            'vdetector',]

group = 'basic'

devices = dict(
)

startupcode = '''
SetDetectors(det)
'''
