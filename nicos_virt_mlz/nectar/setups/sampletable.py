description = 'Sample manipulation stage'

group = 'optional'

excludes = ['servostar']

devices = dict(
    stx = device('nicos.devices.generic.Axis',
        description = 'Sample Translation X',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (0, 1010),
            curvalue = 500,
            unit = 'mm',
        ),
        pollinterval = 5,
        maxage = 12,
        precision = 0.1,
    ),
    sty = device('nicos.devices.generic.Axis',
        description = 'Sample Translation Y',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (0, 580),
            unit = 'mm',
            curvalue = 290,
        ),
        pollinterval = 5,
        maxage = 12,
        precision = 0.1,
    ),
    sry = device('nicos.devices.generic.Axis',
        description = 'Sample Rotation around Y',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-360, 360),
            unit = 'deg',
            curvalue = 0,
        ),
        pollinterval = 5,
        maxage = 12,
        precision = 0.1,
    ),
)
