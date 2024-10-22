description = 'DR Cryostat'

group = 'basic'

includes = [
    'coldvalve', 'magnet', 'ls350', 'cryocon'
]

devices = dict(
    Gas = device('nicos.devices.generic.ManualMove',
        description = 'Gas Level',
        abslimits = (0, 1000000),
        default = 0,
        unit = '',
    ),
    LN = device('nicos.devices.generic.ManualMove',
        description = 'Liquid Nitrogen Level',
        abslimits = (0, 1000000),
        default = 0,
        unit = 'cm',
    ),
    cryostat_20t = device('nicos_mgml.devices.cryostat.Cryostat',
        description = '20T cryostat',
        levelmeter = 'magnet_lhl',
        gasmeter = 'Gas',
        calibration = [(0, 1.5), (29, 4.36), (77.4, 34.5), (100, 36.2)],
        unit = '%',
    ),
)

alias_config = {
    'Cryostat':  {'cryostat_20t': 100},
}
