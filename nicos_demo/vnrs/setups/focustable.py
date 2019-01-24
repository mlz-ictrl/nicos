description = 'Focus manipulation stage'

group = 'lowlevel'

tango_base = 'tango://localhost:10000/st/'

devices = dict(
    focustransm = device('nicos.devices.generic.VirtualMotor',
        description = 'Camera translation motor (focus)',
        speed = 1,
        unit = 'mm',
        fmtstr = '%.2f',
        lowlevel = True,
        abslimits = (0, 300),
    ),
    focustrans = device('nicos.devices.generic.Axis',
        description = 'Camera translation (focus)',
        motor = 'focustransm',
        precision = 0.01,
    ),
)
