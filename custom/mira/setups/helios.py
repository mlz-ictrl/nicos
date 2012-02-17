description = 'Helios 3He analyzer system'
group = 'optional'

devices = dict(
    He_GF = device('nicos.taco.CurrentSupply',
                   tacodevice = 'mira/ttiql/tti2_1',
                   abslimits=(0, 2)),

    pol   = device('nicos.mira.helios.HePolarizer',
                   tacodevice = 'mira/ttiql/tti2_2v'),
)
