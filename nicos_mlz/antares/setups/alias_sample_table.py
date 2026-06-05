description = 'sry environment alias for tomo rotation device'

group = 'lowlevel'

devices = dict(
    sry = device('nicos.devices.generic.DeviceAlias'),
    stx = device('nicos.devices.generic.DeviceAlias'),
    sty = device('nicos.devices.generic.DeviceAlias'),
)
