description = 'Focus rotation ring'

group = 'lowlevel'

devices = dict(
    frr_m = device('nicos.devices.entangle.Motor',
        tangodevice = 'tango://phytron01.nectar.frm2.tum.de:10000/box/frr/mot',
        fmtstr = '%.1f',
        lowlevel = True,
        userlimits = (0., 242.),
    ),
    frr = device('nicos_mlz.nectar.devices.FocusRing',
        description = 'Focus rotation ring',
        precision = 0.01,
        motor = 'frr_m',
        lenses = {
            '85mm': (0, 300),
            '100mm': (0, 360),
            '135mm': (0, 270),
            '200mm': (0, 240),
        }
    ),
)
