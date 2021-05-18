description = 'Secondary slit devices'

group = 'optional'

devices = dict(
    sst = device('nicos.devices.generic.Axis',
        description = 'SST',
        motor = device('nicos.devices.generic.VirtualMotor',
            fmtstr = '%.2f',
            unit = 'mm',
            abslimits = (-15, 15),
            curvalue = 0,
            speed = 1,
        ),
        precision = 0.01,
    ),
    ssw = device('nicos.devices.generic.Axis',
        description = 'Secondary Slit Width',
        motor = device('nicos.devices.generic.VirtualMotor',
            fmtstr = '%.1f',
            unit = 'mm',
            abslimits = (0, 60),
            userlimits = (0, 20),
            curvalue = 0,
            speed = 1,
            requires =  {'level': 'admin'},
        ),
        precision = 0.01,
    ),
)
