description = 'BOA Table 6'

pvprefix = 'SQ:BOA:mcu1:'

devices = dict(
    t6tx = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Table 6 X Translation',
        motorpv = pvprefix + 'T6TX',
        errormsgpv = pvprefix + 'T6TX-MsgTxt',
        precision = 0.05,
        can_disable = True,
    ),
    t6ty = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Table 6 Y Translation',
        motorpv = pvprefix + 'T6TY',
        errormsgpv = pvprefix + 'T6TY-MsgTxt',
        precision = 0.05,
        can_disable = True,
    ),
    Table6 = device('nicos_sinq.boa.devices.boatable.BoaTable',
        description = 'Table 6',
        standard_devices = ['t6tx', 't6ty']
    ),
)
