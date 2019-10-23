description = 'BOA Table 4'

pvprefix = 'SQ:BOA:mcu1:'

devices = dict(
    t4tx = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Table 4 X Translation',
        motorpv = pvprefix + 'T4TX',
        errormsgpv = pvprefix + 'T4TX-MsgTxt',
        precision = 0.05,
    ),
    t4ty = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Table 4 Y Translation',
        motorpv = pvprefix + 'T4TY',
        errormsgpv = pvprefix + 'T4TY-MsgTxt',
        precision = 0.05,
    ),
    Table4 = device('nicos_sinq.boa.devices.boatable.BoaTable',
        description = 'Table 4',
        standard_devices = ['t4tx', 't4ty']
    ),
)
