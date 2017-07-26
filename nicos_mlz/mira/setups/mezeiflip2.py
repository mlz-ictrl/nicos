description = 'Mezei spin flipper using TTI power supply'
group = 'optional'

tango_base = 'tango://mira1.mira.frm2:10000/mira/'

devices = dict(
    dct3 = device('nicos.devices.tango.PowerSupply',
                  description = 'current in first channel of supply (flipper current)',
                  tangodevice = tango_base + 'tti2/out1',
                  timeout = 1,
                  precision = 0.01,
                 ),

    dct4 = device('nicos.devices.tango.PowerSupply',
                  description = 'current in second channel of supply (compensation current)',
                  tangodevice = tango_base + 'tti2/out2',
                  timeout = 1,
                  precision = 0.01,
                 ),

    flipx = device('nicos.devices.polarized.MezeiFlipper',
                   description = 'second Mezei flipper (after sample)',
                   flip = 'dct3',
                   corr = 'dct4',
                  ),

)
