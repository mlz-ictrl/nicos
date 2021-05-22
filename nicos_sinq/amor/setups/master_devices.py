description = 'Temporary setup for the mota controller at AMOR'

includes = ['detector_stage']

devices = dict(
    nu = device('nicos_sinq.amor.devices.logical_motor.DetectorAngleMotor',
        description = 'Intended detector angle',
        com = 'com',
        coz = 'coz',
        coz_scale_factor = 4100,
        unit = '',
    ),
    mu = device('nicos.devices.generic.DeviceAlias', alias = 'som'),
)
