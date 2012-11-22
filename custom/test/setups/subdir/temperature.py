# This file is has overrides from another "temperature.py" in the parent dir.

description = 'virtual temperature device'
group = 'basic'

includes = ['system']

devices = dict(
    T        = device('devices.generic.VirtualTemperature',
                      abslimits = (0, 300),
                      speed = 5,
                      unit = 'K'),
)
