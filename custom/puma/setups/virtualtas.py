description = 'test triple-axis setup'
group = 'basic'

devices = dict(
#    phi      = device('devices.generic.VirtualMotor',
#                      abslimits = (-180, 180),
#                      initval = 0,
#                      unit = 'deg'),

#    psi      = device('devices.generic.VirtualMotor',
#                      abslimits = (0, 360),
#                      initval = 0,
#                      unit = 'deg'),

    mth      = device('devices.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (-180, 180),
                      precision = 0.05,
                      initval = 45),

    mtt      = device('devices.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (-180, 180),
                      precision = 0.05,
                      initval = 90),

#    ath      = device('devices.generic.VirtualMotor',
#                      unit = 'deg',
#                      abslimits = (-180, 180),
#                      precision = 0.05,
#                      initval = 35),

#    att      = device('devices.generic.VirtualMotor',
#                      unit = 'deg',
#                      abslimits = (-180, 180),
#                      precision = 0.05,
#                      initval = 70),
)
