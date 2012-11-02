description = 'Helios 3He analyzer system'
group = 'optional'

devices = dict(
    He_GF = device('devices.taco.CurrentSupply',
                   tacodevice = 'mira/ttiql/tti2_1',
                   abslimits=(0, 2)),

    pol   = device('mira.helios.HePolarizer',
                   tacodevice = 'mira/ttiql/tti2_2v'),
)
