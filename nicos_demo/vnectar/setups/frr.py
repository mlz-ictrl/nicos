description = 'Focus rotation ring'

group = 'lowlevel'

devices = dict(
    frr_m = device('nicos.devices.generic.VirtualMotor',
        fmtstr = '%.1f',
        lowlevel = True,
        abslimits = (0., 360.),
        speed = 25.,
        unit = 'deg',
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
