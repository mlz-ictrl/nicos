description = 'Mezei spin flipper using Lambda Genesys power supply'
group = 'optional'

tango_base = 'tango://antareshw.antares.frm2.tum.de:10000/antares/'

devices = dict(
    dct1 = device('nicos.devices.entangle.PowerSupply',
        description = 'Current 1',
        tangodevice = tango_base + 'lambda1/current',
        abslimits = (0, 5),
    ),
    dct2 = device('nicos.devices.entangle.PowerSupply',
        description = 'Current 2',
        tangodevice = tango_base + 'lambda2/current',
        abslimits = (0, 5),
    ),
    flip = device('nicos.devices.polarized.MezeiFlipper',
        description = 'Mezei flipper before sample (in shielding table)',
        flip = 'dct1',
        corr = 'dct2',
    ),
)

monitor_blocks = dict(
    default = Block('Mezei-Flip',
        [
            BlockRow(
                Field(dev='dct1'),
                Field(dev='dct2'),
                Field(dev='flip', width=5),
            ),
        ],
        setups=setupname,
    ),
)
