description = 'Sample environment alias for magnetic field'

group = 'lowlevel'

devices = dict(
    B = device('nicos.devices.generic.DeviceAlias'),
)

extended = dict(
    representative = 'B',
)

startupcode = '''
AddEnvironment(B)
'''
