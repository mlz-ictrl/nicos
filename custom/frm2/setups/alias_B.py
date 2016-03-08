description = 'Sample environment alias for magnetic field'

group = 'lowlevel'
includes = []

devices = dict(
    B = device('devices.generic.DeviceAlias'),
)

startupcode = '''
AddEnvironment(B)
'''
