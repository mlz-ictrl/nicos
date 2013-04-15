# This setup overrides entries from subdir/cryo.py.
group = 'optional'
description = 'virtual temperature device'

devices = dict(
    T        = device('devices.generic.VirtualTemperature',
                      abslimits = (2, 300),
                      warnlimits = (0, 300),
                      speed = 6,
                      unit = 'K',
                     ),
)
