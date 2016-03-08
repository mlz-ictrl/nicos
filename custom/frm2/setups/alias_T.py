description = 'Sample environment aliases for temperature control'

group = 'lowlevel'
includes = []

devices = dict(
    T  = device('devices.generic.DeviceAlias'),
    Ts = device('devices.generic.DeviceAlias'),
)

startupcode = '''
AddEnvironment(Ts, T)
'''
