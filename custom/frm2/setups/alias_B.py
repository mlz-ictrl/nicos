description = 'Sample environment alias for magnetic field'

includes = []

devices = dict(

    B = device('devices.generic.DeviceAlias',
               description = 'Currently used magnetic field controlling device',
               alias = '',
              ),
)
