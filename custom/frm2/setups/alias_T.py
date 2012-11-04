description = 'Sample environment aliases for temperature control'

includes = []

devices = dict(

    T  = device('devices.generic.DeviceAlias',
                description = 'Currently used sample temperature controlling device',
                alias = '',
               ),

    Ts = device('devices.generic.DeviceAlias',
                description = 'Currently used sample temperature reading device',
                alias = '',
               ),
)
