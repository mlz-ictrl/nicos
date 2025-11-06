description = 'Goniometer Motors'

group = 'lowlevel'
excludes = ['goniometer']

devices = dict(
    # Omega
    ssth_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Omega Axis Motor',
        abslimits = (-180, 180),
        speed = 10,
        unit = 'deg',
        visibility = (),
    ),
    ssth = device('nicos.devices.generic.Axis',
        description = 'Omega Axis Motor',
        motor = 'ssth_m',
        precision = 0.001,
    ),
    # 2 theta
    sstt_m = device('nicos.devices.generic.VirtualMotor',
        description = '2Theta Axis Motor',
        abslimits = (-100, 150),
        speed = 10,
        unit = 'deg',
        visibility = (),
    ),
    sstt = device('nicos.devices.generic.Axis',
        description = '2Theta Axis Motor',
        motor = 'sstt_m',
        precision = 0.001,
    ),
)
