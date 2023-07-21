description = 'MORPHEUS A3/4 motor aliases'

devices = dict(
    a3 = device('nicos.devices.generic.DeviceAlias',
        description = 'Alias for omega',
        alias = 'sth',
        devclass = 'nicos.core.device.Moveable',
    ),
    a4 = device('nicos.devices.generic.DeviceAlias',
        description = 'Alias for two theta',
        alias = 'stt',
        devclass = 'nicos.core.device.Moveable',
    ),
)
