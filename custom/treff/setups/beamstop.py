description = 'Beam stop device'

group = 'lowlevel'

motor_class = 'devices.generic.VirtualMotor'

devices = dict(
    beamstop_m = device(motor_class,
                        description = 'Beam stop position motor',
                        abslimits = (234.33, 277.17),
                        unit = 'mm',
                        lowlevel = True,
                       ),
    beamstop = device('devices.generic.Axis',
                      description = 'Beam stop position',
                      motor = 'beamstop_m',
                      coder = 'beamstop_m',
                      backlash = 0.1,
                      precision = 0.01,
                      fmtstr = '%.2f',
                      unit = 'mm',
                     ),
)
