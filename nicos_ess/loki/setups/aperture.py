description = 'Aperture settings'

group = 'lowlevel'

devices = dict(
    aperture_x=device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description='x position',
        abslimits=(0, 100),
        userlimits=(0, 100),
        fmtstr='%.f',
        unit='mm',
        speed=5,
        requires={'level': 'admin'},
    ),
    aperture_y=device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description='y position',
        abslimits=(0, 100),
        userlimits=(0, 100),
        fmtstr='%.f',
        unit='mm',
        speed=5,
        requires={'level': 'admin'},
    ),
    aperture_width=device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description='width',
        abslimits=(0, 100),
        userlimits=(0, 100),
        fmtstr='%.f',
        unit='mm',
        speed=5,
        requires={'level': 'admin'},
    ),
    aperture_height=device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description='height',
        abslimits=(0, 100),
        userlimits=(0, 100),
        fmtstr='%.f',
        unit='mm',
        speed=5,
        requires={'level': 'admin'},
    ),
    det_offset=device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description='Detector offset',
        abslimits=(0, 100),
        userlimits=(0, 100),
        fmtstr='%.f',
        unit='mm',
        speed=5,
        requires={'level': 'admin'},
    ),
)
