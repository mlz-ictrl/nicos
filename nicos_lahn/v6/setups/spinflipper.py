description = 'spin flipper setup'

group = 'optional'

nameservice = '172.16.1.1'
servername = 'EXV6'

devices = dict(
    FLIP = device('nicos.devices.vendor.caress.base.Driveable',
        unit = 'A',
        abslimits = (0, 1.5),
        nameserver = '%s' % nameservice,
        objname = '%s' % servername,
        config = 'FLIP1_F   105   2    2      10        30.0   0   1.5',
    ),
    COMP = device('nicos.devices.vendor.caress.base.Driveable',
        unit = 'A',
        abslimits = (0, 4),
        nameserver = '%s' % nameservice,
        objname = '%s' % servername,
        config = 'COMP1_F   105   2    2       9        30.0   0   4',
    ),
    mezeiflipper = device('nicos.devices.polarized.MezeiFlipper',
        description = 'spin flipper',
        flip = 'FLIP',
        corr = 'COMP',
        currents = (0.95, 3.12),
    ),
)