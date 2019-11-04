description = 'BOA Translations 1'

pvprefix = 'SQ:BOA:xy1:'

devices = dict(
    tax = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Translation 1 X',
        motorpv = pvprefix + 'TAX',
        errormsgpv = pvprefix + 'TAX-MsgTxt',
    ),
    tay = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Translation 1 Y',
        motorpv = pvprefix + 'TAY',
        errormsgpv = pvprefix + 'TAY-MsgTxt',
    ),
)
