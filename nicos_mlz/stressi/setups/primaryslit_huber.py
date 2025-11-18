description = 'Primary slit Huber automatic'

group = 'optional'

excludes = ['primaryslit_manual', 'primarycoll']

tango_base = 'tango://motorbox03.stressi.frm2.tum.de:10000/box/'

devices = dict(
    psw_m = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'channel3/motor',
        fmtstr = '%.2f',
        speed = 0.5,
        visibility = (),
    ),
    psw_c = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'channel3/coder',
        fmtstr = '%.2f',
        visibility = (),
    ),
    psw = device('nicos.devices.generic.Axis',
        description = 'Primary slit width (Gauge volume width)',
        motor = 'psw_m',
        coder = 'psw_c',
        precision = 0.01,
    ),
    psh_m = device('nicos.devices.entangle.Motor',
        fmtstr = '%.2f',
        tangodevice = tango_base + 'channel4/motor',
        speed = 0.5,
        visibility = (),
    ),
    psh_c = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'channel4/coder',
        fmtstr = '%.2f',
        visibility = (),
    ),
    psh = device('nicos.devices.generic.Axis',
        description = 'Primary slit height (Gauge volume height)',
        motor = 'psh_m',
        coder = 'psh_c',
        precision = 0.01,
    ),
    pss = device('nicos.devices.generic.TwoAxisSlit',
        description = 'Monochromator entry slit',
        horizontal = 'psw',
        vertical = 'psh',
    ),
)
