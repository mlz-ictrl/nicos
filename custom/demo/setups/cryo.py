group = 'optional'
description = 'virtual temperature device'

devices = dict(
    T        = device('devices.generic.DeviceAlias'),
    Ts       = device('devices.generic.DeviceAlias'),

    T_demo   = device('devices.generic.VirtualTemperature',
                      abslimits = (2, 300),
                      warnlimits = (0, 300),
                      speed = 6,
                      unit = 'K',
                     ),
)

startupcode = '''
T.alias = T_demo
Ts.alias = T_demo
'''
