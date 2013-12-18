group = 'optional'
description = 'virtual temperature device'

devices = dict(
    T        = device('devices.generic.DeviceAlias',
                      description = 'Sample temperature control'),
    Ts       = device('devices.generic.DeviceAlias',
                      description = 'Additional sample thermometer'),

    T_demo   = device('devices.generic.virtual.VirtualRealTemperature',
                      description = 'A virtual (but realistic) temperature controller',
                      abslimits = (2, 300),
                      warnlimits = (0, 300),
                      ramp = 60,
                      unit = 'K',
                      jitter = 0,
                     ),
    T_sample = device('devices.generic.ParamDevice',
                      parameter = 'sample',
                      device = 'T_demo',
                      description = 'Temperature of virtual sample',
                     ),

# for testing frm2.ccr module
    T_stick  = device('devices.generic.VirtualTemperature',
                      description = 'Temperature control of the stick',
                      abslimits = (2, 600),
                      warnlimits = (0, 600),
                      speed = 6,
                      unit = 'K',
                     ),

    T_tube   = device('devices.generic.VirtualTemperature',
                      description = 'Temperature control of the cryo tube',
                      abslimits = (0, 300),
                      warnlimits = (0, 300),
                      speed = 6,
                      unit = 'K',
                     ),

    T_ccr    = device('frm2.ccr.CCRControl',
                      description = 'Control device to regulate sample '
                          'temperature via tube and stick heater',
                      stick = 'T_stick',
                      tube = 'T_tube',
                     ),
)

startupcode = '''
T.alias = T_demo
Ts.alias = T_sample
'''
