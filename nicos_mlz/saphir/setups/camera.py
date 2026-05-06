description = 'Radiography camera table'

group = 'optional'

devices = dict(
    ct_x = device('nicos.devices.generic.VirtualMotor',
        description = 'X translation of radiography camera',
        abslimits = (-100, 100),
        speed = 2,
        unit = 'mm',
    ),
    ct_y = device('nicos.devices.generic.VirtualMotor',
        description = 'Y translation of radiography camera',
        abslimits = (-100, 100),
        speed = 2,
        unit = 'mm',
    ),
)
