description = 'sample table devices'

group = 'lowlevel'

includes = ['system']

excludes = ['tas']

devices = dict(
    z     = device('nicos.devices.generic.VirtualMotor',
                   description = 'z axis',
                   fmtstr = '%.2f',
                   abslimits = (-50, 50),
                   jitter = 0.01,
                   speed = 2,
                   unit = 'mm',
                  ),

    y     = device('nicos.devices.generic.VirtualMotor',
                   description = 'y axis',
                   fmtstr = '%.2f',
                   abslimits = (-100, 100),
                   jitter = 0.01,
                   speed = 5,
                   unit = 'mm',
                  ),

    x     = device('nicos.devices.generic.VirtualMotor',
                   description = 'x axis',
                   fmtstr = '%.2f',
                   abslimits = (-750, 150),
                   jitter = 0.01,
                   speed = 10,
                   unit = 'mm',
                  ),

    omega = device('nicos.devices.generic.VirtualMotor',
                   description = 'omega axis',
                   fmtstr = '%.2f',
                   abslimits = (-180, 180),
                   jitter = 0.03,
                   speed = 2,
                   unit = 'deg',
                  ),

    chi   = device('nicos.devices.generic.VirtualMotor',
                   description = 'chi axis',
                   fmtstr = '%.2f',
                   abslimits = (-5, 5),
                   jitter = 0.03,
                   speed = 0.2,
                   unit = 'deg',
                  ),

    phi   = device('nicos.devices.generic.VirtualMotor',
                   description = 'phi axis',
                   fmtstr = '%.2f',
                   abslimits = (-5, 5),
                   jitter = 0.01,
                   speed = 0.2,
                   unit = 'deg',
                  ),
)
