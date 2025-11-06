description = 'Beamstop'

group = 'lowlevel'
excludes = ['beamstop']

devices = dict(
    # x-axis
    sbsx_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Beam stop translation x-Axis motor',
        abslimits = (-50, 50),
        speed = 10,
        unit = 'mm',
        visibility = (),
    ),
    sbsx = device('nicos.devices.generic.Axis',
        description = 'Beam stop translation x-Axis',
        motor = 'sbsx_m',
        precision = 0.001,
    ),
    # y-axis
    sbsy_m = device('nicos.devices.generic.VirtualMotor',
        description = 'Beam stop translation y-Axis motor',
        abslimits = (-50, 50),
        speed = 10,
        unit = 'mm',
        visibility = (),
    ),
    sbsy = device('nicos.devices.generic.Axis',
        description = 'Beam stop translation y-Axis motor',
        motor = 'sbsy_m',
        precision = 0.001,
    ),
)
