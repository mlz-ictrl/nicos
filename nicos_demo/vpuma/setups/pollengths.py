description = 'Lenght devices for polarisation analysis'

group = 'lowlevel'

devices = dict(
    lsd1 = device('nicos.devices.generic.ManualMove',
        description = 'distance sample-deflector 1',
        default = 613,
        unit = 'mm',
        fmtstr = '%.0f',
        abslimits = (0, 1000),
    ),
    lsd2 = device('nicos.devices.generic.ManualMove',
        description = 'distance sample-deflector 2',
        default = 663,
        unit = 'mm',
        fmtstr = '%.0f',
        abslimits = (0, 1000),
    ),
    lpsd = device('nicos.devices.generic.ManualMove',
        description = 'distance sample PSD',
        default = 2316,
        unit = 'mm',
        fmtstr = '%.0f',
        abslimits = (2316, 2316),
    ),
)
