description = 'DR Cryostat'

group = 'basic'

includes = [
    'coldvalve', 'magnet9t', 'ls350', 'cryocon'
]

devices = dict(
    Gas = device('nicos.devices.generic.ManualMove',
        description = 'Gas Level',
        abslimits = (0, 1000000),
        default = 0,
        unit = '',
    ),
    cryostat_9t = device('nicos_mgml.devices.cryostat.Cryostat',
        description = '20T cryostat',
        levelmeter = 'lhe_level',
        gasmeter = 'Gas',
        calibration = [(0, 1.5), (29, 4.36), (77.4, 34.5), (100, 36.2)],
        unit = '%',
    ),
)

alias_config = {
    'Cryostat':  {'cryostat_9t': 100},
}
