description = 'Sample environment aliases for temperature control'

group = 'lowlevel'

devices = dict(
    T = device('nicos.devices.generic.DeviceAlias'),
    Ts = device('nicos.devices.generic.DeviceAlias'),
)

extended = dict(
    representative = 'T',
)

startupcode = '''
AddEnvironment(Ts, T)
'''
