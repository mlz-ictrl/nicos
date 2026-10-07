description = 'Instrument specific distances'

group = 'lowlevel'

devices = dict(
    detsampledist = device('nicos.devices.generic.ManualMove',
        description = 'Distance between sample and detector',
        default = 1375,
        abslimits = (1375, 1375),
        unit = 'mm',
    ),
)
