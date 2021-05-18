description = 'Radialcollimator devices'

group = 'optional'

devices = dict(
    mot1 = device('nicos.devices.generic.VirtualMotor',
        description = 'MOT1',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-200., 200),
        speed = 2,
    ),
    rad_fwhm = device('nicos.devices.generic.ManualMove',
        description = 'FWHM Radialcollimator',
        fmtstr = '%.1f',
        default = 5,
        unit = 'mm',
        abslimits = (0, 20),
        requires = {'level': 'admin'},
    ),
)
