description = 'Instrument specific distances'

group = 'lowlevel'

devices = dict(
    detsampledist = device('nicos.devices.generic.ManualMove',
        description = 'Distance between sample and detector',
        default = 1.375,
        abslimits = (1.375, 1.375),
        unit = 'm',
    ),
)
