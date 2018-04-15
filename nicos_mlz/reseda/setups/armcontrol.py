description = 'Reseda arm controller setup'

group = 'lowlevel'

includes = ['arm_1', 'arm_2']

devices = dict(
    armctrl = device('nicos_mlz.reseda.devices.ArmController',
        description = 'Arm controller',
        arm1 = 'arm1_rot',
        arm2 = 'arm2_rot',
    ),
)
