description = "testing Refsans's slits with virtual devices"

group = 'optional'


devices = dict(
    rsm1 = device('devices.generic.VirtualMotor',
                  description = 'First Refsans SlitMotor',
                  abslimits = (-100, 100),
                  speed = 1,
                  unit = 'mm',
                 ),
    rsm2 = device('devices.generic.VirtualMotor',
                  description = 'Second Refsans SlitMotor',
                  abslimits = (-100, 100),
                  speed = 1,
                  unit = 'mm',
                 ),
    rslit = device('refsans.slits.Slit',
                   description = 'Refsans slit system',
                   first = 'rsm1',
                   second = 'rsm2',
                   leftshapes = dict(bl = (0, 20), K1 = (50, 20), K2 = (-50, 25)),
                   rightshapes = dict(bl = (0, 20), K1 = (50, 20), K2 = (-50, 25)),
                  ),
)
