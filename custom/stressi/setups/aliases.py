description = 'Alias devices for robot and sample table'

group = 'lowlevel'
includes = []

devices = dict(
    tths  = device('devices.generic.DeviceAlias'),
    omgs = device('devices.generic.DeviceAlias'),
    xt = device('devices.generic.DeviceAlias'),
    yt = device('devices.generic.DeviceAlias'),
    zt = device('devices.generic.DeviceAlias'),
)
