description = 'Sample manipulation stage'

group = 'lowlevel'

devices = dict(
    transm = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample translation motor',
        speed = 1,
        unit = 'mm',
        fmtstr = '%.2f',
        lowlevel = True,
        abslimits = (0, 150),
    ),
    trans = device('nicos.devices.generic.Axis',
        description = 'Sample translation',
        motor = 'transm',
        precision = 0.01,
    ),
    rotm = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample rotation motor',
        speed = 1,
        unit = 'deg',
        fmtstr = '%.3f',
        lowlevel = True,
        abslimits = (-360, 360),
    ),
    rot = device('nicos.devices.generic.Axis',
        description = 'Sample rotation',
        motor = 'rotm',
        precision = 0.01,
    ),
)
