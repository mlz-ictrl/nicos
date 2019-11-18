description = 'Focus rotation ring'

group = 'lowlevel'

devices = dict(
    frr_m = device('nicos.devices.tango.Motor',
        tangodevice = 'tango://phytron01.nectar.frm2.tum.de:10000/box/frr/mot',
        fmtstr = '%.1f',
        lowlevel = True,
        userlimits = (0., 242.),
    ),
    frr = device('nicos.devices.generic.Axis',
        description = 'Focus rotation ring',
        precision = 0.01,
        motor = 'frr_m',
    ),
)
