description = 'Detector rotation device'

group = 'lowlevel'

motor_class = 'devices.generic.VirtualMotor'

devices = dict(
    detector_m = device(motor_class,
                        description = 'Detector rotation motor',
                        abslimits = (-180.0, 189.0),
                        unit = 'deg',
                        lowlevel = True,
                       ),
    detector = device('devices.generic.Axis',
                      description = 'Detector rotation position',
                      motor = 'detector_m',
                      coder = 'detector_m',
                      backlash = 0.1,
                      precision = 0.001,
                      fmtstr = '%.2f',
                      unit = 'deg',
                     ),
)
