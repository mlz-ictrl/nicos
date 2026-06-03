description = 'main motors'
group = 'optional'

devices = dict(
    mophi = device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description = 'scattering angle',
        userlimits = (0, 87),
        abslimits = (0, 87),
        speed = 10.,
        unit = 'deg',
        pollinterval = 0.5,
    ),
    mopsi = device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description = 'sample rotation',
        userlimits = (-160, -16),
        abslimits = (-160, -16),
        speed = 10.,
        unit = 'deg',
        pollinterval = 0.5,
    ),
    moana = device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description = 'analyzer position',
        userlimits = (0, 7),
        abslimits = (0, 7),
        speed = 1.,
        unit = 'cm',
        pollinterval = 0.5,
    ),
    mo_z = device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description = 'sample height',
        userlimits = (0, 210),
        abslimits = (0, 210),
        speed = 50.,
        unit = 'mm',
        pollinterval = 0.5,
    ),
    mobeta = device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description = 'simulated motor',
        userlimits = (-10, 10),
        abslimits = (-10, 10),
        speed = 4.,
        unit = '',
        visibility = ('metadata', 'namespace')
    ),
    mogamma = device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description = 'simulated motor',
        userlimits = (-10, 10),
        abslimits = (-10, 10),
        speed = 4.,
        unit = '',
        visibility = ('metadata', 'namespace')
    ),
    mo_wall = device(
        'nicos.devices.generic.virtual.VirtualMotor',
        description = 'Rotates lead wall in front of the sample stage',
        userlimits = (0, 360),
        abslimits = (0, 360),
        speed = 60.,
        unit = 'deg',
        pollinterval = 0.5,
    ),
)
