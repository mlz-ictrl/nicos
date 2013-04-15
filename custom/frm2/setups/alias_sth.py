description = 'Alias for sample rotation devices'

group = 'lowlevel'
includes = []

devices = dict(
    sth  = device('devices.generic.DeviceAlias',
                  description = 'Current sample rotation device'),
)
