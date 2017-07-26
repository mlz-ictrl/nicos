description = 'Alias devices for robot and sample table'

group = 'lowlevel'
includes = []

devices = dict(
    chis = device('nicos.devices.generic.DeviceAlias'),
    phis = device('nicos.devices.generic.DeviceAlias'),
)
