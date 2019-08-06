description = 'Motor for FOV camera translation in large detector box'

group = 'optional'

devices = dict(
    ccdtx = device('nicos.devices.generic.VirtualMotor',
        description = 'Camera Translation X',
        abslimits = (-9999, 9999),
        userlimits = (-0, 693),
        unit = 'mm',
        curvalue = 0,
    ),
)
