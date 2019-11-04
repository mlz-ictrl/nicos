description = 'BOA Translations 2'

pvprefix = 'SQ:BOA:xy2:'

devices = dict(
    tbx = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Translation 2 X',
        motorpv = pvprefix + 'TBX',
        errormsgpv = pvprefix + 'TBX-MsgTxt',
    ),
    tby = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Translation 2 Y',
        motorpv = pvprefix + 'TBY',
        errormsgpv = pvprefix + 'TBY-MsgTxt',
    ),
)
