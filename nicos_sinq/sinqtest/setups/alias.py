description = 'Multiple aliases for testing'

devices = dict(
    alias_1 = device('nicos.core.device.DeviceAlias'),
    alias_2 = device('nicos.core.device.DeviceAlias',
        alias = 'alias_1',
    ),
    alias_3 = device('nicos.core.device.DeviceAlias',
        alias = 'alias_2',
    ),
    alias_4 = device('nicos.core.device.DeviceAlias',
        alias = 'alias_3',
    ),
)
