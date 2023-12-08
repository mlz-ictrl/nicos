description = 'BOA Table 5'

pvprefix = 'SQ:BOA:mcu1:'

devices = dict(
    t5tx = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Table 5 X Translation',
        motorpv = pvprefix + 'T5TX',
        errormsgpv = pvprefix + 'T5TX-MsgTxt',
        precision = 0.05,
        can_disable = True,
    ),
    t5ty = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Table 5 Y Translation',
        motorpv = pvprefix + 'T5TY',
        errormsgpv = pvprefix + 'T5TY-MsgTxt',
        precision = 0.05,
        can_disable = True,
    ),
    Table5 = device('nicos_sinq.boa.devices.boatable.BoaTable',
        description = 'Table 5',
        standard_devices = ['t5tx', 't5ty']
    ),
)
