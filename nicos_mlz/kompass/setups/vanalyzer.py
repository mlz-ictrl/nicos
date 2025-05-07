description = 'Virtual Analyzer devices'

group = 'lowlevel'

excludes = ['analyzer']

devices = dict(
    ana = device('nicos.devices.tas.Monochromator',
        description = 'virtual analyzer',
        unit = 'A-1',
        material = 'PG',
        reflection = (0, 0, 2),
        dvalue = 3.355,
        theta = 'ath',
        twotheta = 'att',
        focush = None,
        focusv = None,
        abslimits = (0.1, 10),
        scatteringsense = 1,
        crystalside = 1,
    ),
    ath = device('nicos.devices.generic.VirtualMotor',
        description = 'virtual analyzer theta',
        unit = 'deg',
        abslimits = (-180, 180),
        precision = 0.05,
    ),
    att = device('nicos.devices.generic.VirtualMotor',
        description = 'virtual analyzer two-theta',
        unit = 'deg',
        abslimits = (-180, 180),
        precision = 0.05,
    ),
)
