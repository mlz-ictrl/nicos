name = 'GUI test setup'

includes = ['stdsystem']

devices = dict(
    gm1 = device('nicos.devices.generic.VirtualMotor',
        unit = 'mm',
        curvalue = 0,
        abslimits = (-100, 100),
        userlimits = (-50, 50),
    ),
    gmalias = device('nicos.devices.generic.DeviceAlias',
        alias = 'gm1',
    ),
    gax = device('nicos.devices.generic.Axis',
        motor = 'gm1',
        coder = None,
        obs = [],
        precision = 0,
        loopdelay = 0.02,
        loglevel = 'debug',
    ),
)
