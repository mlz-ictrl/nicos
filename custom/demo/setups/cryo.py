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

# for testing frm2.ccr module
    T_stick   = device('devices.generic.VirtualTemperature',
                      abslimits = (2, 600),
                      warnlimits = (0, 600),
                      speed = 6,
                      unit = 'K',
                     ),

    T_tube   = device('devices.generic.VirtualTemperature',
                      abslimits = (0, 300),
                      warnlimits = (0, 300),
                      speed = 6,
                      unit = 'K',
                     ),

    T_ccr    = device('frm2.ccr.CCRControl',
                      stick = 'T_stick',
                      tube = 'T_tube',
                     ),
)

startupcode = '''
T.alias = T_demo
Ts.alias = T_demo
'''
