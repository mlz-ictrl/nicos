description = 'BOA Translations 1'

pvprefix = 'SQ:BOA:xy1:'

devices = dict(
    tax = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Translation 1 X',
        motorpv = pvprefix + 'TAX',
        errormsgpv = pvprefix + 'TAX-MsgTxt',
        precision = 0.001
    ),
    tay = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Translation 1 Y',
        motorpv = pvprefix + 'TAY',
        errormsgpv = pvprefix + 'TAY-MsgTxt',
        precision = 0.001
    ),
)
