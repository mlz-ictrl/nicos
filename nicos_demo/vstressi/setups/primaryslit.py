description = 'Primary slit CARESS HWB Devices'

group = 'lowlevel'

devices = dict(
    pst = device('nicos.devices.generic.VirtualMotor',
        description = 'PST',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-100., 100),
        speed = 5,
    ),
    psz = device('nicos.devices.generic.VirtualMotor',
        description = 'PSZ',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-100., 100),
        speed = 5,
    ),
)
