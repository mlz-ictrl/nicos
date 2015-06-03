description = 'Mezei spin flipper using TTI power supply'
group = 'optional'

devices = dict(
    dct1 = device('devices.tango.PowerSupply',
                  description = 'current in first channel of supply (flipper current)',
                  tangodevice = 'tango://mira1.mira.frm2:10000/mira/tti1/out1',
                  abslimits = (0, 5),
                  timeout = 1,
                  precision = 0.01,
                 ),

    dct2 = device('devices.tango.PowerSupply',
                  description = 'current in second channel of supply (compensation current)',
                  tangodevice = 'tango://mira1.mira.frm2:10000/mira/tti1/out2',
                  abslimits = (0, 5),
                  timeout = 1,
                  precision = 0.01,
                 ),

    flip = device('devices.polarized.MezeiFlipper',
                  description = 'Mezei flipper before sample (in shielding table)',
                  flip = 'dct1',
                  corr = 'dct2',
                 ),

)
