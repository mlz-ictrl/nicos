description = 'Mezei spin flipper using Lambda Genesys power supply'
group = 'optional'

tango_base = 'tango://antareshw.antares.frm2:10000/antares/'

devices = dict(
    dct1 = device('devices.tango.PowerSupply',
        description = 'Current 1',
        tangodevice = tango_base + 'lambda1/current',
        abslimits = (0, 5),
        lowlevel = False,
    ),
    dct2 = device('devices.tango.PowerSupply',
        description = 'Current 2',
        tangodevice = tango_base + 'lambda2/current',
        abslimits = (0, 5),
        lowlevel = False,
    ),
    flip = device('devices.polarized.MezeiFlipper',
        description = 'Mezei flipper before sample (in shielding table)',
        flip = 'dct1',
        corr = 'dct2',
    ),
)
