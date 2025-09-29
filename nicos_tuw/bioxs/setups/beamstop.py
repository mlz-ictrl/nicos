description = 'Beamstop'

group = 'lowlevel'

tangobase = 'tango://bioxs:10000/motor/'

devices = dict(
    # x-axis
    bsx_m = device('nicos.devices.entangle.Motor',
        description = 'Beam stop translation x-Axis motor',
        tangodevice = tangobase + 'RS485/bsx_motor',
        visibility = (),
    ),
    bsx = device('nicos.devices.generic.Axis',
        description = 'Beam stop translation x-Axis',
        motor = 'bsx_m',
        precision = 0.001,
    ),
    # y-axis
    bsy_m = device('nicos.devices.entangle.Motor',
        description = 'Beam stop translation y-Axis motor',
        tangodevice = tangobase + 'RS485/bsy_motor',
        visibility = (),
    ),
    bsy = device('nicos.devices.generic.Axis',
        description = 'Beam stop translation y-Axis motor',
        motor = 'bsy_m',
        precision = 0.001,
    ),
)
