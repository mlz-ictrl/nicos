# -*- coding: utf-8 -*-

description = 'Polarizer motor devices and flipper'
group = 'optional'

tango_base = 'tango://phys.treff.frm2:10000/treff/'

devices = dict(
    pflipper = device('nicos_mlz.jcns.devices.polarizer.DOFlipper',
        description = 'Polarizer flipper',
        tangodevice = tango_base + 'FZJDP_Digital/pflipper',
        mapping = {
            'up': 1,
            'down': 0,
        },
        powersupplies = ['pow4grad', 'pow4hf'],
    ),
    polarizer_tilt = device('nicos.devices.entangle.Motor',
        description = 'Polarizer tilt',
        tangodevice = tango_base + 'FZJS7/polarizer_tilt',
        unit = 'deg',
        precision = 0.01,
        fmtstr = '%.3f',
    ),
    polarizer_y = device('nicos.devices.entangle.Motor',
        description = 'Polarizer y translation',
        tangodevice = tango_base + 'FZJS7/polarizer_y',
        unit = 'mm',
        precision = 0.01,
        fmtstr = '%.2f',
    ),
    pow4hf = device('nicos.devices.entangle.PowerSupply',
        description = 'Power supply 4 current control ch 1',
        tangodevice = tango_base + 'toellner/pow4hf',
        voltage = 32.0,  # pflipper down
    ),
    pow4grad = device('nicos.devices.entangle.PowerSupply',
        description = 'Power supply 4 current control ch 2',
        tangodevice = tango_base + 'toellner/pow4grad',
        voltage = 17.66,
    ),
)
