description = 'Motors for the Detector'

group = 'lowlevel'

devices = dict(
    detx = device('nicos.devices.generic.VirtualMotor',
        description = 'Detector X Translation',
        precision = 0.5,
        unit = 'mm',
        abslimits = (-0, 18800),
        speed = 16000,
        offset = -1532,
    ),
    dety = device('nicos.devices.generic.VirtualMotor',
        description = 'Detector Y Translation',
        precision = 0.2,
        unit = 'mm',
        abslimits = (-0, 490),
        speed = 8000,
    ),
    detphi = device('nicos.devices.generic.VirtualMotor',
        description = 'Detector Rotation',
        precision = 0.2,
        unit = 'deg',
        abslimits = (0, 180),
        speed = 2000,
    ),
)
