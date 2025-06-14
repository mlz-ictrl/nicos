description = 'BOA Translations 2'

pvprefix = 'SQ:BOA:xy2:'

devices = dict(
    tbx = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Translation 2 X',
        motorpv = pvprefix + 'TBX',
        errormsgpv = pvprefix + 'TBX-MsgTxt',
        precision = 0.001
    ),
    tby = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Translation 2 Y',
        motorpv = pvprefix + 'TBY',
        errormsgpv = pvprefix + 'TBY-MsgTxt',
        precision = 0.001
    ),
)
