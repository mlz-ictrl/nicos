description = 'Sample environment aliases for temperature control'

group = 'lowlevel'
includes = []

devices = dict(

    T  = device('devices.generic.DeviceAlias',
                description = 'Current sample temperature controller'),

    Ts = device('devices.generic.DeviceAlias',
                description = 'Current sample temperature sensor'),
)
