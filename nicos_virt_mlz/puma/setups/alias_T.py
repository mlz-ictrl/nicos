description = 'Sample environment alias for magnetic field'

group = 'lowlevel'

devices = dict(
    T = device('nicos.devices.generic.DeviceAlias'),
    Ts = device('nicos.devices.generic.DeviceAlias'),
)

startupcode = '''
AddEnvironment(T, Ts)
'''
