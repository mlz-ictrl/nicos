description = 'Helios 3He analyzer system'
group = 'optional'

devices = dict(
    He_GF = device('devices.taco.CurrentSupply',
                   description = 'Guide field for Helios cell',
                   tacodevice = '//mirasrv/mira/ttiql/tti2_1',
                   abslimits = (0, 2),
                  ),

    pol   = device('mira.helios.HePolarizer',
                   description = 'Polarization direction of Helios cell with RF flipper',
                   tacodevice = '//mirasrv/mira/ttiql/tti2_2v',
                  ),
)
