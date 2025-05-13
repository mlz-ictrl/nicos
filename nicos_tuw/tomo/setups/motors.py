description = 'motors that are available by default'

group = 'optional'
excludes = ['motor_sim']
tangobase = 'tango://localhost:10000/box/'

devices = dict(
    sample_Rz_m = device('nicos.devices.entangle.Motor',
        description = 'capillary translation Rz-axis motor',
        tangodevice = tangobase + 'phymotion/Rz_motor',
        visibility = (),
    ),
    sample_Rz = device('nicos.devices.generic.Axis',
        description = 'capillary translation y-axis',
        motor = 'sample_Rz_m',
        precision = 0.001,
    ),
)
