description = 'STRESS-SPEC setup with Eulerian cradle plus small xyz table'

group = 'basic'

includes = [
    'eulerian',
]

devices = dict(
    xe = device('nicos.devices.generic.Axis',
        description = 'X Eulerian XYZ',
        fmtstr = '%.2f',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-75, 75),
            unit = 'mm',
            speed = 1,
            fmtstr = '%.2f',
        ),
        precision = 0.01,
    ),
    ye = device('nicos.devices.generic.Axis',
        description = 'Y Eulerian XYZ',
        fmtstr = '%.2f',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-75, 75),
            unit = 'mm',
            speed = 1,
            fmtstr = '%.2f',
        ),
        precision = 0.01,
    ),
    ze = device('nicos.devices.generic.Axis',
        description = 'Z Eulerian XYZ',
        fmtstr = '%.2f',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (0.5, 25),
            unit = 'mm',
            speed = 1,
            fmtstr = '%.2f',
            curvalue = 0.5,
        ),
        precision = 0.01,
    ),
)
