description = 'Focus manipulation stage'

group = 'lowlevel'

tango_base = 'tango://localhost:10000/st/'

devices = dict(
    focusm = device('nicos.devices.entangle.Motor',
        description = 'Camera focus motor (translation)',
        tangodevice = tango_base + 'focus/motor',
        unit = 'mm',
        fmtstr = '%.2f',
        lowlevel = True,
    ),
    focus = device('nicos.devices.generic.Axis',
        description = 'Camera focus (translation)',
        motor = 'focusm',
        precision = 0.01,
    ),
)
