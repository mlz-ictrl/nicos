description = 'manual move devices'

group = 'lowlevel'

devices = dict(
    sa2 = device('nicos.devices.generic.ManualMove',
        description = 'sample aperture 2',
        unit = 'mm',
        fmtstr = '%.0f',
        default = 0,
        warnlimits = (1, 50),
        abslimits = (0, 50)
    ),
)
