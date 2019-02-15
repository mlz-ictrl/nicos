description = 'Alias devices for robot and sample table'

group = 'lowlevel'

devices = dict(
    chis = device('nicos.devices.generic.DeviceAlias'),
    phis = device('nicos.devices.generic.DeviceAlias'),
)
