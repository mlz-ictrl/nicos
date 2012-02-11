description = 'analyzer table'

devices = dict(
    ath      = device('nicos.taco.Axis',
                      description = 'analyzer theta',
                      tacodevice = 'mira/axis/ath',
                      abslimits = (90 - 90, 90 + 90),
                      fmtstr = '%.3f',
                      offset = 90.0),
    att      = device('nicos.taco.Axis',
                      description = 'analyzer two-theta',
                      tacodevice = 'mira/axis/att',
                      abslimits = (-90 - 135, -90 + 135),
                      fmtstr = '%.2f',
                      offset = -90.0),

    ana      = device('nicos.tas.Monochromator',
                      unit = 'A-1',
                      theta = 'ath',
                      twotheta = 'att',
                      focush = None,
                      focusv = None,
                      abslimits = (0, 10),
                      dvalue = 3.355),

    adr      = device('nicos.taco.Axis',
                      description = 'analyzer detector rotation',
                      tacodevice = 'mira/axis/adr',
                      abslimits = (-180, 180),
                      fmtstr = '%.3f'),
)
