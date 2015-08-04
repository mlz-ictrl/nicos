description = 'Alias for sample rotation devices'

group = 'lowlevel'
includes = []

devices = dict(
    sth  = device('devices.generic.DeviceAlias',
                  # provide a sensible default for mira
                  alias = 'om',
    ),
)
