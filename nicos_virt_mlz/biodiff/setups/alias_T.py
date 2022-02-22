description = 'Sample environment aliases for temperature control'

group = 'lowlevel'

devices = dict(
    T = device('nicos.devices.generic.DeviceAlias'),
    Ts = device('nicos.devices.generic.DeviceAlias'),
)

startupcode = '''
AddEnvironment(Ts, T)
'''
