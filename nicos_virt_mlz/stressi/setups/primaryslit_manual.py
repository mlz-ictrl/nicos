description = 'Primary slit manual adjustment'

group = 'optional'

includes = ['primaryslit']

excludes = ['primaryslit_huber', 'primarycoll']

devices = dict(
    psw = device('nicos.devices.generic.VirtualMotor',
        description = 'Primary Slit Width (Gauge volume width)',
        fmtstr = '%.2f',
        curvalue = 50,
        unit = 'mm',
        abslimits = (0, 70),
        # requires = {'level': 'admin'},
    ),
    psh = device('nicos.devices.generic.VirtualMotor',
        description = 'Primary Slit Height (Gauge volume height)',
        fmtstr = '%.2f',
        curvalue = 50,
        unit = 'mm',
        abslimits = (0, 150),
        # requires = {'level': 'admin'},
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
