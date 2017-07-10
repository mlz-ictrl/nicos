description = 'virtual POLI lifting counter'

group = 'lowlevel'

devices = dict(
    liftingctr = device('nicos.devices.generic.VirtualMotor',
                      description = 'lifting counter axis',
                      pollinterval = 15,
                      maxage = 61,
                      fmtstr = '%.2f',
                      abslimits = (-4.2, 30),
                      precision = 0.01,
                      unit = 'deg',
                     ),
)
