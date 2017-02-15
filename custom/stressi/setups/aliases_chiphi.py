description = 'Alias devices for robot and sample table'

group = 'lowlevel'
includes = []

devices = dict(
    chis = device('devices.generic.DeviceAlias'),
    phis = device('devices.generic.DeviceAlias'),
)
