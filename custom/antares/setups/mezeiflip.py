description = 'Mezei spin flipper using Lambda Genesys power supply'
group = 'optional'

devices = dict(
    dct1 = device('devices.taco.CurrentSupply',
                  description = 'Current 1',
                  tacodevice = '//antaressrv/antares/lambda/out1',
                  abslimits = (0, 5),
                  lowlevel = False,
                 ),

    dct2 = device('devices.taco.CurrentSupply',
                  description = 'Current 2',
                  tacodevice = '//antaressrv/antares/lambda/out2',
                  abslimits = (0, 5),
                  lowlevel = False,
                 ),

    flip = device('devices.polarized.MezeiFlipper',
                  description = 'Mezei flipper before sample (in shielding table)',
                  flip = 'dct1',
                  corr = 'dct2',
                 ),

)
