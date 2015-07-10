description = 'Mezei spin flipper using TTI power supply'
group = 'optional'

devices = dict(
    dct3 = device('devices.tango.PowerSupply',
                  description = 'current in first channel of supply (flipper current)',
                  tangodevice = 'tango://mira1.mira.frm2:10000/mira/tti2/out1',
                  abslimits = (0, 5),
                 ),

    dct4 = device('devices.tango.PowerSupply',
                  description = 'current in second channel of supply (compensation current)',
                  tangodevice = 'tango://mira1.mira.frm2:10000/mira/tti2/out2',
                  abslimits = (0, 5),
                 ),

    flipx = device('devices.polarized.MezeiFlipper',
                   description = 'second Mezei flipper (after sample)',
                   flip = 'dct3',
                   corr = 'dct4',
                  ),

)
