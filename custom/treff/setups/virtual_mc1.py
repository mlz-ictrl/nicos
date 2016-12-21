description = '(MC 1)'

group = 'optional'

motor_class = 'devices.generic.VirtualMotor'

devices = dict(
    mc1_rot = device(motor_class,
                     description = 'MC1 rotation motor',
                     precision = 0.01,
                     unit = 'deg',
                     abslimits = (-88.62, 169.523),
                    ),
    mc1_x   = device(motor_class,
                     description = 'MC1 x motor',
                     precision = 0.01,
                     abslimits = (0, 100),
                     unit = 'mm',
                    ),
)
