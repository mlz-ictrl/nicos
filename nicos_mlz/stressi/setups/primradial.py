description = 'Radialcollimator devices incoming beam'

group = 'optional'

includes = ['primaryslit']

excludes = ['primaryslit_manual', 'primaryslit_huber']

tango_base = 'tango://motorbox03.stressi.frm2.tum.de:10000/box/'

devices = dict(
    rcm_m = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'channel8/motor',
        fmtstr = '%.3f',
        visibility = (),
    ),
    rcm_c = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'channel8/coder',
        fmtstr = '%.3f',
        visibility = (),
    ),
    rcm = device('nicos.devices.generic.Axis',
        description = 'Primary radial collimator horizontal tilt (RadColli=ZE)',
        fmtstr = '%.3f',
        motor = 'rcm_m',
        coder = 'rcm_c',
        precision = 0.01,
    ),
    psw = device('nicos.devices.generic.Axis',
        description = 'Primary radial collimator width (Gauge volume width)',
        motor = device('nicos.devices.generic.ManualSwitch',
            fmtstr = '%.1f',
            unit = 'mm',
            states = (1, 2, 5),
        ),
        precision = 0.1,
        requires = {'level': 'admin'},
    ),
    psh = device('nicos.devices.generic.Axis',
        description = 'Primary radial collimator height (Gauge volume height)',
        motor = device('nicos.devices.generic.ManualSwitch',
            fmtstr = '%.1f',
            unit = 'mm',
            states = (3, 5),
        ),
        precision = 0.1,
        requires = {'level': 'admin'},
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
