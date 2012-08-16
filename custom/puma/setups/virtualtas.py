description = 'test triple-axis setup'
group = 'basic'

devices = dict(
#    phi      = device('nicos.generic.VirtualMotor',
#                      abslimits = (-180, 180),
#                      initval = 0,
#                      unit = 'deg'),

    psi      = device('nicos.generic.VirtualMotor',
                      abslimits = (0, 360),
                      initval = 0,
                      unit = 'deg'),

    mth      = device('nicos.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (-180, 180),
                      precision = 0.05,
                      initval = 45),

    mtt      = device('nicos.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (-180, 180),
                      precision = 0.05,
                      initval = 90),

    ath      = device('nicos.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (-180, 180),
                      precision = 0.05,
                      initval = 35),

    att      = device('nicos.generic.VirtualMotor',
                      unit = 'deg',
                      abslimits = (-180, 180),
                      precision = 0.05,
                      initval = 70),
)
