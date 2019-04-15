description = 'pressure sensors connected to the chambers'

group = 'lowlevel'

devices = dict(
    chamber_CB = device('nicos.devices.generic.ManualMove',
        description = 'pressure sensor connected to the CB',
        default = 1.7e-6,
        abslimits = (0, 1000),
        pollinterval = 10,
        maxage = 12,
        unit = 'mbar',
        fmtstr = '%.1g',
    ),
    chamber_SFK = device('nicos.devices.generic.ManualMove',
        description = 'pressure sensor connected to the SFK',
        default = 1.7e-6,
        abslimits = (0, 1000),
        pollinterval = 10,
        maxage = 12,
        unit = 'mbar',
    ),
    chamber_SR = device('nicos.devices.generic.ManualMove',
        description = 'pressure sensor connected to the SR',
        default = 1.7e-6,
        abslimits = (0, 1000),
        pollinterval = 10,
        maxage = 12,
        unit = 'mbar',
    ),
)
