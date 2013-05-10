description = 'sample table devices'

group = 'lowlevel'

includes = ['system', ]

devices = dict(
    z    = device('devices.generic.VirtualMotor',
                  fmtstr = '%.2f',
                  abslimits = (-50, 50),
                  jitter = 0.01,
                  speed = 2,
                  unit = 'mm',
                 ),

    y    = device('devices.generic.VirtualMotor',
                  fmtstr = '%.2f',
                  abslimits = (-100, 100),
                  jitter = 0.01,
                  speed = 5,
                  unit = 'mm',
                 ),

    x    = device('devices.generic.VirtualMotor',
                  fmtstr = '%.2f',
                  abslimits = (-750, 150),
                  jitter = 0.01,
                  speed = 10,
                  unit = 'mm',
                 ),

    omega = device('devices.generic.VirtualMotor',
                   fmtstr = '%.2f',
                   abslimits = (-180, 180),
                   jitter = 0.03,
                   speed = 2,
                   unit = 'deg',
                  ),

    chi = device('devices.generic.VirtualMotor',
                 fmtstr = '%.2f',
                 abslimits = (-5, 5),
                 jitter = 0.03,
                 speed = 0.2,
                 unit = 'deg',
                ),

    phi = device('devices.generic.VirtualMotor',
                 fmtstr = '%.2f',
                 abslimits = (-5, 5),
                 jitter = 0.01,
                 speed = 0.2,
                 unit = 'deg',
                ),
)
