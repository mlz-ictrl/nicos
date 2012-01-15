name = 'analyzer table'

devices = dict(
    ath      = device('nicos.taco.Axis',
                      tacodevice = 'mira/axis/ath',
                      abslimits = (90 - 90, 90 + 90),
                      fmtstr = '%.3f',
                      offset = 90.0),
    att      = device('nicos.taco.Axis',
                      tacodevice = 'mira/axis/att',
                      abslimits = (-90 - 135, -90 + 135),
                      fmtstr = '%.2f',
                      offset = -90.0),
    adr      = device('nicos.taco.Axis',
                      tacodevice = 'mira/axis/adr',
                      abslimits = (-180, 180),
                      fmtstr = '%.3f'),
)
