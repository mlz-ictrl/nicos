group = 'optional'
description = 'virtual temperature device'

devices = dict(
    T        = device('devices.generic.DeviceAlias'),
    Ts       = device('devices.generic.DeviceAlias'),

    T_demo   = device('devices.generic.virtual.VirtualRealTemperature',
                      description = 'A virtual (but realistic) temperature controller',
                      abslimits = (2, 1000),
                      warnlimits = (0, 325),
                      ramp = 60,
                      unit = 'K',
                      jitter = 0,
                      precision = 0.1,
                     ),
    T_sample = device('devices.generic.ReadonlyParamDevice',
                      parameter = 'sample',
                      device = 'T_demo',
                      description = 'Temperature of virtual sample',
                     ),
)

startupcode = '''
T.alias = T_demo
Ts.alias = T_sample
'''
