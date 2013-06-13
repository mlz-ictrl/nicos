description = 'Aliases for sample translation/rotation'

group = 'lowlevel'

includes = []

devices = dict(
    stx  = device('devices.generic.DeviceAlias',
                  description = 'Sample translation along X'
           ),
    sty  = device('devices.generic.DeviceAlias',
                  description = 'Sample translation along Y'
           ),
    sry  = device('devices.generic.DeviceAlias',
                  description = 'Sample rotation around Y'
           ),
)
