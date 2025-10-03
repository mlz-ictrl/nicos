description = 'BOA Table 4'

pvprefix = 'SQ:BOA:turboPmac1:'

devices = dict(
    t4tx = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Table 4 X Translation',
        motorpv = pvprefix + 'T4TX',
    ),
    t4ty = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Table 4 Y Translation',
        motorpv = pvprefix + 'T4TY',
        can_disable = True,
    ),
    Table4 = device('nicos_sinq.devices.componenttable.ComponentTable',
        description = 'Table 4',
        standard_devices = ['t4tx', 't4ty']
    ),
)
