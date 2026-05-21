description = 'Radial collimator devices'

group = 'lowlevel'

devices = dict(
    rc = device('nicos_mlz.erwin.devices.rc.RadialCollimator',
        description = 'Radial collimator',
        motor = 'rc_motor',
        frequency = 0.05,
    ),
    rc_motor = device('nicos.devices.generic.VirtualMotor',
        description = 'Radial collimator motor',
        abslimits = (-float('inf'), float('inf')),
        unit = 'deg',
        speed = 10,
        visibility = (),
    ),
)
