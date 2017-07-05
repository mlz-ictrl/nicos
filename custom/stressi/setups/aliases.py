description = 'Alias devices for robot and sample table'

group = 'lowlevel'
includes = []

devices = dict(
    tths  = device('nicos.devices.generic.DeviceAlias'),
    omgs = device('nicos.devices.generic.DeviceAlias'),
    xt = device('nicos.devices.generic.DeviceAlias'),
    yt = device('nicos.devices.generic.DeviceAlias'),
    zt = device('nicos.devices.generic.DeviceAlias'),
)
