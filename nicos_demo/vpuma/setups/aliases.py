description = 'Device aliases'

group = 'lowlevel'

devices = dict(
    ana = device('nicos.devices.generic.DeviceAlias',
        description = 'analyser alias device',
        devclass = 'nicos.devices.tas.Monochromator',
    ),
    theta = device('nicos.devices.generic.DeviceAlias',
        description = 'analyser angle',
        devclass = 'nicos.core.Readable',
    ),
)
