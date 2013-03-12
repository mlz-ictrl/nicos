# This setup overrides entries from subdir/cryo.py.
group = 'optional'

devices = dict(
    T        = device('devices.generic.VirtualTemperature',
                      abslimits = (2, 300),
                      speed = 6,
                      unit = 'K',
                     ),
)
