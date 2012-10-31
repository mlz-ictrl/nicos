descripion = 'Sample environment magnet aliases'

includes = []

devices = dict(

    B = device('nicos.generic.DeviceAlias',
               description = 'Alias to the currently used magnetic field controlling device',
               alias = '',
              ),
)
