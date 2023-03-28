description = 'Sample table devices'

group = 'lowlevel'

devices = dict(
    x = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample translation X',
        abslimits = (-100, 100),
        fmtstr = '%.2f',
        speed = 1,
        unit = 'mm',
    ),
    y = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample translation Y',
        abslimits = (-100, 100),
        fmtstr = '%.2f',
        speed = 1,
        unit = 'mm',
    ),
    z = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample translation Z',
        abslimits = (0, 100),
        fmtstr = '%.2f',
        speed = 0.5,
        unit = 'mm',
    ),
)
