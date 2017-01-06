description = 'Analyzer device'

group = 'lowlevel'

motor_class = 'devices.generic.VirtualMotor'

devices = dict(
    analyzer_tilt_m = device(motor_class,
                             description = 'Analyzer tilt motor',
                             abslimits = (-16.667, 16.667),
                             unit = 'deg',
                             lowlevel = True,
                            ),
    analyzer_tilt = device('devices.generic.Axis',
                           description = 'Analyzer tilt',
                           motor = 'analyzer_tilt_m',
                           coder = 'analyzer_tilt_m',
                           backlash = 0.1,
                           precision = 0.001,
                           fmtstr = '%.3f',
                           unit = 'deg',
                          ),
)
