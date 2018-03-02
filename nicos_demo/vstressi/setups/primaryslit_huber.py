description = 'Primary slit Huber automatic'

group = 'optional'

devices = dict(
    psw = device('nicos.devices.generic.VirtualMotor',
        description = 'PSW',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-100., 100),
        speed = 5,
    ),
    psh = device('nicos.devices.generic.VirtualMotor',
        description = 'PSH',
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (-100., 100),
        speed = 5,
    ),
)
