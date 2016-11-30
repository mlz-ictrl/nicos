description = 'virtual POLI lifting counter'

group = 'lowlevel'

devices = dict(
    liftingctr = device('devices.generic.VirtualMotor',
                      description = 'lifting counter axis',
                      pollinterval = 15,
                      maxage = 61,
                      fmtstr = '%.2f',
                      abslimits = (-5, 30),
                      precision = 0.01,
                      unit = 'deg',
                     ),
)
