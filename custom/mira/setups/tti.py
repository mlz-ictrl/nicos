description = 'TTI power supplies'
group = 'optional'

devices = dict(
    dct1 = device('devices.taco.CurrentSupply',
                  tacodevice = 'mira/ttiql/tti1_1',
                  abslimits=(0, 5)),

    dct2 = device('devices.taco.CurrentSupply',
                  tacodevice = 'mira/ttiql/tti1_2',
                  abslimits=(0, 5)),

    flip = device('mira.flipper.Flipper',
                  flip = 'dct1',
                  corr = 'dct2'),

#    dct3 = device('devices.taco.CurrentSupply',
#                  tacodevice = 'mira/ttiql/tti2_1',
#                  abslimits=(0, 5)),

#    dct4 = device('devices.taco.CurrentSupply',
#                  tacodevice = 'mira/ttiql/tti2_2',
#                  abslimits=(0, 5)),

)
