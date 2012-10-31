descripion = 'Sample environment temperature aliases'

includes = []

devices = dict(

    T = device('nicos.generic.DeviceAlias',
               description = 'Alias to the currently used sample temperature controlling device',
               alias = '',
              ),
    Ts = device('nicos.generic.DeviceAlias',
               desription = 'Alias to the currently used sample temperature reading device',
              ),
)
