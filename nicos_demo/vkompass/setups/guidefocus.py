description = 'Neutron guide focussing devices'

group = 'lowlevel'

devices = dict(
    lguide = device('nicos.devices.generic.Axis',
        description = 'Long table position',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-3.5, 208.5),
            unit = 'mm',
        ),
        fmtstr = '%.2f',
        precision = 0.05,
    ),
    sguide = device('nicos.devices.generic.Axis',
        description = 'Short table position',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (-10.1, 210.1),
            unit = 'mm',
        ),
        fmtstr = '%.2f',
        precision = 0.05,
    ),
    guide = device('nicos.devices.generic.MultiSwitcher',
        description = 'Neutron guide selector',
        moveables = ['sguide', 'lguide'],
        mapping = {
            'straight': [205.037, 208.5],
            'focussing': [0., -3.5],
        },
        fallback = 'undefined',
        fmtstr = '%s',
        precision = [0.05, 0.05],
        blockingmove = False,
        unit = '',
    ),
)
