description = 'Focus manipulation stage'

group = 'lowlevel'

tango_base = 'tango://localhost:10000/st/'

devices = dict(
    focustransm = device('nicos.devices.tango.Motor',
        description = 'Camera translation motor (focus)',
        tangodevice = tango_base + 'y/motor',
        unit = 'mm',
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    focustrans = device('nicos.devices.generic.Axis',
        description = 'Camera translation (focus)',
        motor = 'focustransm',
        precision = 0.01,
    ),
)
