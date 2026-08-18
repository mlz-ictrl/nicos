description = 'Instrument specific distances'

group = 'lowlevel'

devices = dict(
    detsampledist = device('nicos.devices.generic.ManualMove',
        description = 'Distance between sample and detector',
        default = 1.117,
        abslimits = (1.117, 1.117),
        unit = 'm',
    ),
)
