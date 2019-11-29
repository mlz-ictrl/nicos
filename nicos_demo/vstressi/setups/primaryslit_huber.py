description = 'Primary slit Huber automatic'

group = 'optional'

excludes = ['primaryslit_manual', 'primarycoll']

devices = dict(
    psw_m = device('nicos.devices.generic.VirtualMotor',
        fmtstr = '%.2f',
        unit = 'mm',
        speed = 0.5,
        abslimits = (0, 7),
        lowlevel = True,
    ),
    psw_c = device('nicos.devices.generic.VirtualCoder',
        motor = 'psw_m',
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    psw = device('nicos.devices.generic.Axis',
        description = 'Primary slit width, horizontal opening (PSW)',
        motor = 'psw_m',
        coder = 'psw_c',
        precision = 0.01,
    ),
    psh_m = device('nicos.devices.generic.VirtualMotor',
        fmtstr = '%.2f',
        unit = 'mm',
        speed = 0.5,
        abslimits = (0, 17),
        lowlevel = True,
    ),
    psh_c = device('nicos.devices.generic.VirtualCoder',
        motor = 'psh_m',
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    psh = device('nicos.devices.generic.Axis',
        description = 'Primary slit height, vertical opening (PSH)',
        motor = 'psh_m',
        coder = 'psh_c',
        precision = 0.01,
    ),
)
