description = 'setup for the velocity selector'
group = 'optional'

devices = dict(
    selector_speed = device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description = 'Selector speed',
        abslimits = (3100, 31000),
        userlimits = (3100, 31000),
        speed = 5000,
        unit = 'rpm',
        precision = 10,
        fmtstr = '%.0f',
    ),
)
