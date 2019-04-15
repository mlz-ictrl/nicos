description = "sc2 height after nok9"

group = 'lowlevel'

devices = dict(
    sc2 = device('nicos.devices.generic.VirtualMotor',
        description = 'sc2 Motor',
        abslimits = (-150, 150),
        speed = 1.,
        unit = 'mm',
        # refpos = -7.2946,
    ),
)
