description = 'Alias configuration'

display_order = 30

devices = dict(
    sgl = device('nicos.core.device.DeviceAlias',
        description = 'Alias goniometer lower',
    ),
    sgu = device('nicos.core.device.DeviceAlias',
        description = 'Alias goniometer upper',
    ),
)
