description = 'Standa devices'

setup = 'optional'

tango_base = 'tango://motorbox10.spodi.frm2.tum.de:10000/box/'

devices = dict(
    std_rot = device('nicos.devices.generic.Axis',
        description = 'Rotation stage',
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + 'std_rot/motor',
            visibility = (),
        ),
        precision = 0.01,
    ),
    std_x = device('nicos.devices.generic.Axis',
        description = 'X translation stage',
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + 'std_x/motor',
        ),
        precision = 0.01,
    ),
    std_y = device('nicos.devices.generic.Axis',
        description = 'Y translation stage',
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + 'std_y/motor',
        ),
        precision = 0.01,
    ),
    std_z = device('nicos.devices.generic.Axis',
        description = 'Z translation stage',
        motor = device('nicos.devices.entangle.Motor',
            tangodevice = tango_base + 'std_z/motor',
        ),
        precision = 0.01,
    ),
)
