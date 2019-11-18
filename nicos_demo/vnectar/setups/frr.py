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
    ),
)
