description = 'Helios 3He analyzer system'
group = 'optional'

devices = dict(
    He_GF = device('nicos.devices.taco.CurrentSupply',
                   description = 'guide field for Helios cell',
                   tacodevice = '//mirasrv/mira/ttiql/tti2_1',
                   abslimits = (0, 2),
                  ),

    pol   = device('nicos_mlz.mira.devices.helios.HePolarizer',
                   description = 'polarization direction of Helios cell with RF flipper',
                   tacodevice = '//mirasrv/mira/ttiql/tti2_2v',
                  ),
)
