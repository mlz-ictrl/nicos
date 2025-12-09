description = 'Sample manipulation stage using servostar controller'
group = 'optional'

devices = dict(
    stx = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample Translation X',
        abslimits = (0, 1010),
        speed = 5,
        unit = 'mm',
    ),
    sty = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample Translation Y',
        abslimits = (0, 580),
        unit = 'mm',
        speed = 5,
    ),
    sry = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample Rotation around Y',
        abslimits = (0, 360),
        speed = 5,
        unit = 'deg',
    ),
)
