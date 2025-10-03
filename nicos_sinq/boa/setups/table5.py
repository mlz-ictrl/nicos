description = 'BOA Table 5'

pvprefix = 'SQ:BOA:turboPmac1:'

devices = dict(
    t5tx = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Table 5 X Translation',
        motorpv = pvprefix + 'T5TX',
    ),
    t5ty = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        description = 'Table 5 Y Translation',
        motorpv = pvprefix + 'T5TY',
    ),
    Table5 = device('nicos_sinq.devices.componenttable.ComponentTable',
        description = 'Table 5',
        standard_devices = ['t5tx', 't5ty']
    ),
)
