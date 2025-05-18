description = 'motors that are available by default'

group = 'optional'

tangobase = 'tango://localhost:10000/box/'

devices = dict(
    sry_m = device('nicos.devices.entangle.Motor',
        description = 'Sample rotation y-Axis motor',
        tangodevice = tangobase + 'phymotion/Rz_motor',
        visibility = (),
    ),
    sry = device('nicos.devices.generic.Axis',
        description = 'Sample rotation y-Axis',
        motor = 'sry_m',
        precision = 0.001,
    ),
)
