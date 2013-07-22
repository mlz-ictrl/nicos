description = 'Mezei spin flipper using TTI power supply'
group = 'optional'

devices = dict(
    dct3 = device('devices.taco.CurrentSupply',
                  tacodevice = '//mirasrv/mira/ttiql/tti2_1',
                  abslimits=(0, 5)),

    dct4 = device('devices.taco.CurrentSupply',
                  tacodevice = '//mirasrv/mira/ttiql/tti2_2',
                  abslimits=(0, 5)),

    flipx = device('mira.flipper.Flipper',
                  flip = 'dct3',
                  corr = 'dct4'),

)
