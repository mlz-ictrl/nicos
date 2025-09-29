description = 'Beamstop'

group = 'lowlevel'
excludes = ['beamstop']

devices = dict(
    # x-axis
    bsx_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Beam stop translation x-Axis motor',
        abslimits = (-50, 50),
        speed = 10,
        unit = 'mm',
        visibility = (),
    ),
    bsx = device('nicos.devices.generic.Axis',
        description = 'Beam stop translation x-Axis',
        motor = 'bsx_m',
        precision = 0.001,
    ),
    # y-axis
    bsy_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Beam stop translation y-Axis motor',
        abslimits = (-50, 50),
        speed = 10,
        unit = 'mm',
        visibility = (),
    ),
    bsy = device('nicos.devices.generic.Axis',
        description = 'Beam stop translation y-Axis motor',
        motor = 'bsy_m',
        precision = 0.001,
    ),
)
