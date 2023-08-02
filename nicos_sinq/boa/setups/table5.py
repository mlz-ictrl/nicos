description = 'BOA Table 5'

pvprefix = 'SQ:BOA:mcu1:'

devices = dict(
    t5tx = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Table 5 X Translation',
        motorpv = pvprefix + 'T5TX',
        errormsgpv = pvprefix + 'T5TX-MsgTxt',
        precision = 0.05,
    ),
    t5ty = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Table 5 Y Translation',
        motorpv = pvprefix + 'T5TY',
        errormsgpv = pvprefix + 'T5TY-MsgTxt',
        precision = 0.05,
    ),
    Table5 = device('nicos_sinq.boa.devices.boatable.BoaTable',
        description = 'Table 5',
        standard_devices = ['t5tx', 't5ty']
    ),
)
