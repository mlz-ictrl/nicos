description = 'motors moving the pinhole in front of the SDD.'

group = 'lowlevel'

tangobase = 'tango://localhost:10000/box/'

devices = dict(
    pin_Ty_m = device('nicos.devices.entangle.Motor',
        description = 'pinhole translation y-axis motor',
        tangodevice = tangobase + 'pinhole/Ty_Motor',
        visibility = (),
    ),
    pin_Ty = device('nicos.devices.generic.Axis',
        description = 'pinhole translation y-axis',
        motor = 'pin_Ty_m',
        precision = 0.01,
    ),
    pin_Tz_m = device('nicos.devices.entangle.Motor',
        description = 'pinhole translation z-axis motor',
        tangodevice = tangobase + 'pinhole/Tz_Motor',
        visibility = (),
    ),
    pin_Tz = device('nicos.devices.generic.Axis',
        description = 'pinhole translation z-axis',
        motor = 'pin_Tz_m',
        precision = 0.01,
    ),
)
