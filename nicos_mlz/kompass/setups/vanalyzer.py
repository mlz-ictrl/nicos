description = 'Virtual Analyzer devices'

group = 'lowlevel'

excludes = ['analyzer']

devices = dict(
    ana = device('nicos.devices.tas.Monochromator',
        description = 'virtual analyzer',
        unit = 'A-1',
        dvalue = 3.355,
        theta = 'vath',
        twotheta = 'vatt',
        focush = None,
        focusv = None,
        abslimits = (0.1, 10),
        scatteringsense = 1,
        crystalside = 1,
    ),
    ath = device('nicos.devices.generic.VirtualMotor',
        description = 'virtual analysator theta',
        unit = 'deg',
        abslimits = (-180, 180),
        precision = 0.05,
    ),
    att = device('nicos.devices.generic.VirtualMotor',
        description = 'virtual analysator two-theta',
        unit = 'deg',
        abslimits = (-180, 180),
        precision = 0.05,
    ),
)
