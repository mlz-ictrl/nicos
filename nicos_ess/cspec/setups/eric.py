description = 'ESS source'

group = 'lowlevel'

devices = dict(
    accel = device('nicos.devices.generic.ManualSwitch',
        description = "ERIC's LINAC status",
        states = ['on', 'off'],
    ),
    ecurrent = device('nicos.devices.generic.VirtualMotor',
        description = "ERIC's LINAC current",
        curvalue = 60,
        jitter = 0.5,
        abslimits = (0.5, 100),
        unit = 'mA',
    ),
    power = device('nicos.devices.generic.VirtualMotor',
        description = "ERIC's LINAC power",
        curvalue = 4.5,
        jitter = 0.3,
        abslimits = (0, 5),
        unit = 'MW',
        fmtstr = '%.2f',
    ),
    lightshutter = device('nicos.devices.generic.ManualSwitch',
        description = 'Shutter close to moderator',
        states = ['open', 'closed']
    ),
)
