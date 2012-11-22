# This setup overrides entries from subdir/temperature.py.

devices = dict(
    T        = device('devices.generic.VirtualTemperature',
                      abslimits = (0, 300),
                      speed = 6,
                      unit = 'K'),
)
