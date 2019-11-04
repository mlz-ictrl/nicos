description = 'Translation TAZ'

pvprefix = 'SQ:BOA:taz:'

devices = dict(
    taz = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'TAZ translation',
        motorpv = pvprefix + 'TAZ',
        errormsgpv = pvprefix + 'TAZ-MsgTxt',
    ),
)
