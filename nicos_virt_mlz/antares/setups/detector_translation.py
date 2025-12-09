description = 'Detector Table Experimental Chamber 1'

group = 'lowlevel'

devices = dict(
    dtx = device('nicos.devices.generic.VirtualMotor',
        description = 'Detector Translation X',
        abslimits = (0, 730),
        unit = 'mm',
    ),
    dty = device('nicos.devices.generic.VirtualMotor',
        description = 'Detector Translation Y',
        abslimits = (0, 300),
        unit = 'mm',
    ),
)
