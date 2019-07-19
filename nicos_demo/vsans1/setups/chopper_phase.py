description = 'setup for the astrium chopper phase'

group = 'optional'

excludes = ['chopper']

devices = dict(
    chopper_ch1_phase = device('nicos.devices.generic.ManualMove',
        description = 'Chopper channel 1 phase',
        fmtstr = '%.2f',
        maxage = 35,
        abslimits = (-180, 180),
        unit = 'deg',
    ),
    chopper_ch2_phase = device('nicos.devices.generic.ManualMove',
        description = 'Chopper channel 2 phase',
        fmtstr = '%.2f',
        maxage = 35,
        abslimits = (-180, 180),
        unit = 'deg',
    ),
    chopper_ch1_parkingpos = device('nicos.devices.generic.ManualMove',
        description = 'Chopper channel 1 parking position',
        fmtstr = '%.2f',
        maxage = 35,
        abslimits = (-180, 180),
        unit = '',
    ),
    chopper_ch2_parkingpos = device('nicos.devices.generic.ManualMove',
        description = 'Chopper channel 2 parking position',
        fmtstr = '%.2f',
        maxage = 35,
        abslimits = (-180, 180),
        unit = '',
    )
)
