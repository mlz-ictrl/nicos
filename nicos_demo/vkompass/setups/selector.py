description = 'Selector related devices'

group = 'lowlevel'

devices = dict(
    nvslift_ax = device('nicos.devices.generic.Axis',
        description = 'Selector lift position',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (0, 406),
            unit = 'mm',
        ),
        fmtstr = '%.2f',
        precision = 0.1,
    ),
    nvslift = device('nicos.devices.generic.Switcher',
        description = 'Neutron selector lift',
        moveable = 'nvslift_ax',
        mapping = {'out': 0.,
                   'in': 405.377},
        fallback = '',
        fmtstr = '%s',
        precision = 1.0,
        blockingmove = False,
        unit = 'mm',
    ),
)
