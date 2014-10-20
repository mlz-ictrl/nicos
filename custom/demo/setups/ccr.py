group = 'optional'
description = 'for testing the frm2.ccr module'

devices = dict(
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
