description = 'virtual psi rotation axis'

group = 'optional'

devices = dict(
    psi_virtual = device('nicos.devices.generic.VirtualMotor',
        description = 'virtual rotation axis',
        pollinterval = 15,
        maxage = 61,
        fmtstr = '%.2f',
        abslimits = (-90, 90),
        precision = 0.01,
        unit = 'deg',
    ),
)
