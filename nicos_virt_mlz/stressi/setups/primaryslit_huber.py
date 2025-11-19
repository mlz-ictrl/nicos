description = 'Primary slit Huber automatic'

group = 'optional'

includes = ['primaryslit']

excludes = ['primaryslit_manual', 'primarycoll']

devices = dict(
    psw_m = device('nicos.devices.generic.VirtualMotor',
        fmtstr = '%.2f',
        unit = 'mm',
        speed = 0.5,
        abslimits = (0, 7),
        visibility = (),
    ),
    psw_c = device('nicos.devices.generic.VirtualCoder',
        motor = 'psw_m',
        fmtstr = '%.2f',
        visibility = (),
    ),
    psw = device('nicos.devices.generic.Axis',
        description = 'Primary Slit Width (Gauge volume width)',
        motor = 'psw_m',
        coder = 'psw_c',
        precision = 0.01,
    ),
    psh_m = device('nicos.devices.generic.VirtualMotor',
        fmtstr = '%.2f',
        unit = 'mm',
        speed = 0.5,
        abslimits = (0, 17),
        visibility = (),
    ),
    psh_c = device('nicos.devices.generic.VirtualCoder',
        motor = 'psh_m',
        fmtstr = '%.2f',
        visibility = (),
    ),
    psh = device('nicos.devices.generic.Axis',
        description = 'Primary Slit Height (Gauge volume height)',
        motor = 'psh_m',
        coder = 'psh_c',
        precision = 0.01,
    ),
    pss = device('nicos_mlz.stressi.devices.OffCenteredTwoAxisSlit',
        description = 'Monochromator entry slit',
        horizontal = 'psw',
        vertical = 'psh',
        x = 'pst',
        y = 'psz',
        autodevice_visibility = {'metadata', },
    ),
)
