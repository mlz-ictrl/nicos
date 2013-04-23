group = 'optional'
description = 'virtual temperature device'

includes = ['alias_t']

devices = dict(
    T        = device('devices.generic.VirtualTemperature',
                      abslimits = (2, 300),
                      warnlimits = (0, 300),
                      speed = 6,
                      unit = 'K',
                     ),
)
