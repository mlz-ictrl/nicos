description = 'MasterMACS test motors'

display_order = 26

pvprefix = 'SQ:SINQTEST:masterMacs1:'

devices = dict(
    lin1_mm = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Linear motor 1',
        motorpv = pvprefix + 'lin1',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    rot1_mm = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Rotary motor 1',
        motorpv = pvprefix + 'rot1',
        visibility = ('devlist', 'metadata', 'namespace'),
    ),
    rot1_mm_velo = device('nicos.devices.generic.ParamDevice',
        description = 'Velocity mode for motor rot1',
        device = 'rot1_mm',
        parameter = 'velocity_move',
        copy_status = True,
    ),
)
