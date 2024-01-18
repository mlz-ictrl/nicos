description = 'Translation TAZ'

pvprefix = 'SQ:BOA:taz:'

devices = dict(
    taz = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'TAZ translation',
        motorpv = pvprefix + 'TAZ',
        errormsgpv = pvprefix + 'TAZ-MsgTxt',
    ),
)
