# -*- coding: utf-8 -*-

description = 'Polarizer motor devices and flipper'
group = 'optional'

tango_base = 'tango://phys.treff.frm2:10000/treff/'

devices = dict(
    pflipper = device('nicos.devices.tango.NamedDigitalOutput',
        description = "Flipper",
        tangodevice = tango_base + 'FZJDP_Digital/pflipper',
        mapping = {
            'up': 1,
            'down': 0,
        }
    ),
    polarizer_tilt = device('nicos.devices.tango.Motor',
        description = 'Polarizer tilt',
        tangodevice = tango_base + 'FZJS7/polarizer_tilt',
        unit = 'deg',
        precision = 0.01,
        fmtstr = '%.3f',
    ),
    polarizer_y = device('nicos.devices.tango.Motor',
        description = 'Polarizer y translation',
        tangodevice = tango_base + 'FZJS7/polarizer_y',
        unit = 'mm',
        precision = 0.01,
        fmtstr = '%.2f',
    ),
)
