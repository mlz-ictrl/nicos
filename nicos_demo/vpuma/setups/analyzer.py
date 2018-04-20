description = 'Analyzer devices'

group = 'lowlevel'

devices = dict(
    ath = device('nicos.devices.generic.VirtualMotor',
        description = 'analyzer rocking angle',
        unit = 'deg',
        abslimits = (-0, 60),
        precision = 0.05,
        speed = 0.5,
    ),
    att = device('nicos.devices.generic.VirtualMotor',
        description = 'analyzer scattering angle',
        unit = 'deg',
        abslimits = (-117, 117),
        precision = 0.05,
        speed = 0.5,
    ),
    ana_pg002 = device('nicos.devices.tas.Monochromator',
        description = 'PG-002 analyzer',
        unit = 'A-1',
        theta = 'ath',
        twotheta = 'att',
        reltheta = True,
        focush = None,
        focusv = None,
        abslimits = (1, 5),
        dvalue = 3.355,
        scatteringsense = -1,
        crystalside = -1,
    ),
)
