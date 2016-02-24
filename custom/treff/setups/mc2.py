description = '(MC 2)'

group = 'lowlevel'

motor_class = 'devices.generic.VirtualMotor'

devices = dict(
    mc2_rot_m = device(motor_class,
                       description = 'MC2 rotation motor',
                       abslimits = (-88.62, 169.523),
                       unit = 'deg',
                       lowlevel = True
                      ),
    mc2_rot = device('devices.generic.Axis',
                     description = 'MC2 rotation',
                     motor = 'mc2_rot_m',
                     coder = 'mc2_rot_m',
                     precision = 0.01,
                     backlash = 1.286,
                     fmtstr = '%.3f',
                     unit = 'deg',
                    ),
    mc2_tilt_pg_m = device(motor_class,
                           description = 'MC2 tilt PG motor',
                           abslimits = (-32.68, 32.68),
                           unit = 'deg',
                           lowlevel = True
                          ),
    mc2_tilt_pg = device('devices.generic.Axis',
                         description = 'MC2 tilt PG',
                         motor = 'mc2_tilt_pg_m',
                         coder = 'mc2_tilt_pg_m',
                         precision = 0.001,
                         backlash = 0.07,
                         fmtstr = '%.3f',
                         unit = 'deg',
                        ),
    mc2_tilt_nb_m = device(motor_class,
                           description = 'MC2 tilt NB motor',
                           abslimits = (-32.68, 32.68),
                           unit = 'deg',
                           lowlevel = True
                          ),
    mc2_tilt_nb = device('devices.generic.Axis',
                         description = 'MC2 tilt NB',
                         motor = 'mc2_tilt_nb_m',
                         coder = 'mc2_tilt_nb_m',
                         precision = 0.001,
                         backlash = 0.07,
                         fmtstr = '%.3f',
                         unit = 'deg',
                        ),
)
