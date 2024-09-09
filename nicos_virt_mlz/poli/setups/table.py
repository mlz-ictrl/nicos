description = 'POLI sample table'

group = 'lowlevel'

includes = []

devices = dict(
    sth = device('nicos.devices.generic.DeviceAlias',
        alias = 'omega',
    ),
    omega = device('nicos.devices.generic.VirtualMotor',
        description = 'table omega axis',
        unit = 'deg',
        fmtstr = '%.2f',
        abslimits = (-180, 180),
        speed = 5.625,
    ),
    gamma = device('nicos.devices.generic.VirtualMotor',
        description = 'table gamma axis',
        unit = 'deg',
        fmtstr = '%.2f',
        abslimits = (-20, 130),
        speed = 3.125,
    ),
    chi1 = device('nicos.devices.generic.VirtualMotor',
        description = 'table chi1 axis',
        unit = 'deg',
        fmtstr = '%.2f',
        abslimits = (-5, 5),
        speed = 0.5,
    ),
    chi2 = device('nicos.devices.generic.VirtualMotor',
        description = 'table chi2 axis',
        unit = 'deg',
        fmtstr = '%.2f',
        abslimits = (-5, 5),
        speed = 1.3,
    ),
    xtrans = device('nicos.devices.generic.VirtualMotor',
        description = 'table x translation axis',
        unit = 'mm',
        fmtstr = '%.2f',
        abslimits = (-15, 15),
        speed = 2.5,
    ),
    ytrans = device('nicos.devices.generic.VirtualMotor',
        description = 'table y translation axis',
        unit = 'mm',
        fmtstr = '%.2f',
        abslimits = (-15, 15),
        speed = 2.5,
    ),
)

alias_config = {
    'sth': {'omega': 100}
}
