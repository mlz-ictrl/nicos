description = 'Radial collimator devices diffracted beam'

group = 'optional'

excludes = ['secondaryslit']

devices = dict(
    # mot1 = device('nicos.devices.generic.VirtualMotor',
    #     description = 'MOT1',
    #     fmtstr = '%.2f',
    #     unit = 'mm',
    #     abslimits = (-200., 200),
    #     speed = 2,
    # ),
    rcd_m = device('nicos.devices.generic.VirtualMotor',
        fmtstr = '%.3f',
        abslimits = (-10, 10),
        unit = 'deg',
        visibility = (),
    ),
    rcd = device('nicos.devices.generic.Axis',
        description = 'Secondary radial collimator horizontal tilt (RadColli=ZE)',
        fmtstr = '%.3f',
        motor = 'rcdet_m',
        precision = 0.01,
    ),
    ssw = device('nicos.devices.generic.ManualSwitch',
        description = 'Secondary radial collimator width (Gauge volume depth)',
        fmtstr = '%.1f',
        unit = 'mm',
        states = (0.5, 1, 2, 5, 10, 20),
    ),
    yss = device('nicos.devices.generic.ManualMove',
        description = 'Distance sample detector collimator',
        default = 1100.,
        fmtstr = '%.2f',
        unit = 'mm',
        abslimits = (800, 1300),
    ),
)
