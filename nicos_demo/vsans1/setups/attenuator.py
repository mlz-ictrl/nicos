description = 'attenuator'

group = 'lowlevel'

devices = dict(
    att = device('nicos_mlz.sans1.devices.collimotor.Sans1ColliSwitcher',
        description = 'Attenuator',
        mapping = dict(open=-2, x1000=92.8, x100=187.8, x10=282.8, dia10=377.8),
        moveable = 'att_m',
        blockingmove = False,
        pollinterval = 15,
        maxage = 60,
        precision = 0.1,
        fmtstr = '%s',
    ),
    att_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Attenuator motor',
        unit = 'mm',
        abslimits = (-400, 600),
        lowlevel = True,
    ),
)
