description = 'Goniometer Motors'

group = 'lowlevel'
excludes = ['goniometer']

devices = dict(
    # Omega
    sth_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Omega Axis Motor',
        abslimits = (-180, 180),
        speed = 10,
        unit = 'deg',
        visibility = (),
    ),
    sth = device('nicos.devices.generic.Axis',
        description = 'Omega Axis Motor',
        motor = 'sth_m',
        precision = 0.001,
    ),
    # 2 theta
    stt_m = device('nicos.devices.generic.VirtualMotor',
        description = '2Theta Axis Motor',
        abslimits = (-100, 150),
        speed = 10,
        unit = 'deg',
        visibility = (),
    ),
    stt = device('nicos.devices.generic.Axis',
        description = '2Theta Axis Motor',
        motor = 'stt_m',
        precision = 0.001,
    ),
)
