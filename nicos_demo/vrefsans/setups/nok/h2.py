description = 'Slit H2 using Beckhoff controllers'

group = 'lowlevel'

devices = dict(
    h2_center = device('nicos.devices.generic.VirtualMotor',
        description = 'Horizontal slit system: offset of the slit-center to the beam',
        unit = 'mm',
        abslimits = (-69.5, 69.5),
        speed = 1.,
    ),
    h2_width = device('nicos.devices.generic.VirtualMotor',
        description = 'Horizontal slit system: opening of the slit',
        unit = 'mm',
        abslimits = (0.05, 69.5),
        speed = 1.,
    ),
)
