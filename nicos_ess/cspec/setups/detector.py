description = 'Detector pot devices'

group = 'lowlevel'

devices = dict(
    vacdet = device('nicos.devices.generic.VirtualMotor',
        description = 'Vacuum sensor in detector pot',
        abslimits = (0, 1000),
        pollinterval = 10,
        maxage = 12,
        unit = 'mbar',
        curvalue = 5.1e-4,
        fmtstr = '%.2e',
        jitter = 1.e-5,
    ),
    hv = device('nicos.devices.generic.VirtualMotor',
        description = 'Detector HV power supply',
        requires = {'level': 'admin'},
        abslimits = (0, 1600),
        ramp = 120,
        unit = 'V',
    ),
    ar_flow = device('nicos.devices.generic.VirtualMotor',
        description = 'Argon flow in detector pot',
        abslimits = (0, 100),
        pollinterval = 10,
        maxage = 12,
        unit = 'l/min',
        curvalue = 11.3,
        fmtstr = '%.2f',
        jitter = 3,
    ),
)
