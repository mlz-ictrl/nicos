name = 'Helios He polarizer system'

devices = dict(
    He_GF = device('nicos.taco.CurrentSupply',
                   tacodevice = 'mira/ttiql/tti2_1',
                   abslimits=(0, 2)),

    pol   = device('nicos.mira.helios.HePolarizer',
                   tacodevice = 'mira/ttiql/tti2_2v'),
)
