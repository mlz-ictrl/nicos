description = 'alias for wave length'

group = 'lowlevel'

devices = dict(
    wl = device('nicos.devices.generic.DeviceAlias',
        devclass='nicos.core.Readable'
    ),
)
