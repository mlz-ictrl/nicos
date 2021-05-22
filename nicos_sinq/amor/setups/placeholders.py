description = 'Placeholders for devices not yet present.'

group = 'lowlevel'

devices = dict(
    xs = device('nicos.devices.generic.VirtualMotor',
        description = 'Sample x position',
        abslimits = (0, 730),
        unit = 'mm',
        curvalue = 2500
    ),
    xd2 = device('nicos.devices.generic.VirtualMotor',
        description = 'Diaphragm2 x position',
        abslimits = (0, 3000),
        unit = 'mm',
        curvalue = 2000
    ),
    xl = device('nicos.devices.generic.VirtualMotor',
        description = 'Deflector x position',
        abslimits = (-500, 2000),
        unit = 'mm',
        curvalue = 1500
    ),
    mu_offset = device('nicos.devices.generic.VirtualMotor',
        description = 'Offset on the angle of incidence (deflector mode)',
        abslimits = (-1000, 1000),
        unit = 'mm',
        curvalue = 0
    ),
    kappa = device('nicos.devices.generic.VirtualMotor',
        description = 'Inclination of the beam after the Selene guide',
        abslimits = (-.5, 0),
        unit = '',
        curvalue = -0.2
    ),
    xd3 = device('nicos.devices.generic.VirtualMotor',
        description = 'Diaphragm3 x position',
        abslimits = (2000, 5000),
        unit = 'mm',
        curvalue = 3000
    ),
    soz_ideal = device('nicos.devices.generic.VirtualMotor',
        description = 'Ideal sample stage z (deflector mode)',
        abslimits = (2000, 5000),
        unit = 'mm',
        curvalue = 3000
    ),
)
