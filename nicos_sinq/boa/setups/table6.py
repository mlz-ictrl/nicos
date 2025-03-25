description = 'BOA Table 6'

pvprefix = 'SQ:BOA:turboPmac1:'

devices = dict(
    t6tx = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Table 6 X Translation',
        motorpv = pvprefix + 'T6TX',
    ),
    t6ty = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Table 6 Y Translation',
        motorpv = pvprefix + 'T6TY',
    ),
    Table6 = device('nicos_sinq.devices.componenttable.ComponentTable',
        description = 'Table 6',
        standard_devices = ['t6tx', 't6ty']
    ),
)
