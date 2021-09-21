description = 'Virtual sample environment'

excludes = ['se']

devices = dict(
    B = device('nicos.devices.generic.CalibratedMagnet',
               description = 'Magnet field',
               currentsource = 'current_source',
               calibration = (0.1, 0.0, 0.0, 0.0, 0.0),
               ),
    current_source = device('nicos.devices.generic.VirtualMotor',
                            description = 'Current source for magnet field',
                            abslimits = (0, 15),
                            speed = 0.9,
                            lowlevel = True,
                            unit = 'A'),
)
