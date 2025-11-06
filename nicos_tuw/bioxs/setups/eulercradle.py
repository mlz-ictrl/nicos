description = 'motors from the huber euler cradle'

group = 'optional'

tango_base_motor = 'tango://bioxs:10000/bioxs/motor/'

devices = dict(
    # x-axis
    tex_m = device('nicos.devices.entangle.Motor',
        description = 'Sample translation x-Axis motor',
        tangodevice = tango_base_motor + 'tex_motor',
        visibility = (),
    ),
    tex = device('nicos.devices.generic.Axis',
        description = 'Sample translation x-Axis motor',
        motor = 'tex_m',
        precision = 0.001,
    ),
    # y-axis
    tey_m = device('nicos.devices.entangle.Motor',
        description = 'Sample translation y-Axis motor',
        tangodevice = tango_base_motor + 'tey_motor',
        visibility = (),
    ),
    tey = device('nicos.devices.generic.Axis',
        description = 'Sample translation y-Axis motor',
        motor = 'tey_m',
        precision = 0.001,
    ),
    # z-axis
    tez_m = device('nicos.devices.entangle.Motor',
        description = 'Sample translation z-Axis motor',
        tangodevice = tango_base_motor + 'tez_motor',
        visibility = (),
    ),
    tez = device('nicos.devices.generic.Axis',
        description = 'Sample translation z-Axis motor',
        motor = 'tez_m',
        precision = 0.001,
    ),
    # Chi-axis
    phi_m = device('nicos.devices.entangle.Motor',
        description = 'Sample Rotation phi-Axis motor',
        tangodevice = tango_base_motor + 'phi_motor',
        visibility = (),
    ),
    phi = device('nicos.devices.generic.Axis',
        description = 'Sample Rotation phi-Axis motor',
        motor = 'phi_m',
        precision = 0.001,
    ),
    # Phi-axis
    chi_m = device('nicos.devices.entangle.Motor',
        description = 'Sample Rotation chi-Axis motor',
        tangodevice = tango_base_motor + 'chi_motor',
        visibility = (),
    ),
    chi = device('nicos.devices.generic.Axis',
        description = 'Sample Rotation chi-Axis motor',
        motor = 'chi_m',
        precision = 0.001,
    ),
)
