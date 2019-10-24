description = 'Focus manipulation stage'

group = 'lowlevel'

tango_base = 'tango://localhost:10000/st/'

devices = dict(
    focusm = device('nicos.devices.generic.VirtualMotor',
        description = 'Camera focus motor (translation)',
        speed = 1,
        unit = 'mm',
        fmtstr = '%.2f',
        lowlevel = True,
        abslimits = (0, 300),
    ),
    focus = device('nicos.devices.generic.Axis',
        description = 'Camera focus (translation)',
        motor = 'focusm',
        precision = 0.01,
    ),
)
