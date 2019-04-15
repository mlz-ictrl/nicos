description = 'Funktionsgenerator HP33220'

group = 'optional'

devices = dict(
    hp33220a_1_freq = device('nicos.devices.generic.ManualMove',
        description = 'freq of wave1',
        abslimits = (0, 1e6),
        unit = 'Hz',
    ),
    hp33220a_1_amp = device('nicos.devices.generic.ManualMove',
        description = 'amp of wave1',
        abslimits = (0, 10),
        unit = 'A',
    ),
)
