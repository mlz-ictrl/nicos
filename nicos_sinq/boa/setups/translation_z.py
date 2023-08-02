description = 'Translation TAZ'

pvprefix = 'SQ:BOA:taz:'

devices = dict(
    taz = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'TAZ translation',
        motorpv = pvprefix + 'TAZ',
        errormsgpv = pvprefix + 'TAZ-MsgTxt',
    ),
)
