description = 'Mezei spin flipper using TTI power supply'
group = 'optional'

devices = dict(
    dct3 = device('devices.taco.CurrentSupply',
                  description = 'current in first channel of supply (flipper current)',
                  tacodevice = '//mirasrv/mira/ttiql/tti2_1',
                  abslimits = (0, 5),
                 ),

    dct4 = device('devices.taco.CurrentSupply',
                  description = 'current in second channel of supply (compensation current)',
                  tacodevice = '//mirasrv/mira/ttiql/tti2_2',
                  abslimits = (0, 5),
                 ),

    flipx = device('devices.polarized.MezeiFlipper',
                   description = 'second Mezei flipper (after sample)',
                   flip = 'dct3',
                   corr = 'dct4',
                  ),

)
