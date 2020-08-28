description = 'detector table translation setup'

group = 'lowlevel'

devices = dict(
    stt = device('nicos.devices.generic.Axis',
        description = '2 theta axis moving detector arm',
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (15, 160),
            unit = 'deg',
            speed = 1,
        ),
        precision = 0.01,
        fmtstr = '%.2f',
    ),
    lsd = device("nicos.devices.generic.Axis",
        description = "detector arm translation",
        motor = device('nicos.devices.generic.VirtualMotor',
            abslimits = (900, 1500),
            unit = 'mm',
            speed = 1,
        ),
        precision = 0.01,
        fmtstr = "%.2f",
    ),
)
