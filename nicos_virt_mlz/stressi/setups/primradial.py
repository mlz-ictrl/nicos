description = 'Radial collimator devices incoming beam'

group = 'optional'

includes = ['primaryslit']

excludes = ['primaryslit_huber', 'primaryslit_manual']

devices = dict(
    rcm_m = device('nicos.devices.generic.VirtualMotor',
        fmtstr = '%.3f',
        abslimits = (-10, 10),
        unit = 'deg',
        visibility = (),
    ),
    rcm = device('nicos.devices.generic.Axis',
        description = 'Primary radial collimator horizontal tilt (RadColli=ZE)',
        fmtstr = '%.3f',
        motor = 'rcm_m',
        precision = 0.01,
    ),
    psw = device('nicos_mlz.stressi.devices.PreciseManualSwitch',
        description = 'Primary radial collimator width (Gauge volume width)',
        fmtstr = '%.1f',
        unit = 'mm',
        states = (1, 2, 5),
        # requires = {'level': 'admin'},
    ),
    psh = device('nicos_mlz.stressi.devices.PreciseManualSwitch',
        description = 'Primary radial collimator height (Gauge volume height)',
        fmtstr = '%.1f',
        unit = 'mm',
        states = (3, 5),
        # requires = {'level': 'admin'},
    ),
    pss = device('nicos_mlz.stressi.devices.OffCenteredTwoAxisSlit',
        description = 'Monochromator entry slit',
        horizontal = 'psw',
        vertical = 'psh',
        x = 'pst',
        y = 'pst',
        autodevice_visibility = {'metadata', },
    ),
)
