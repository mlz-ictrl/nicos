description = 'Translation TAZ'

pvprefix = 'SQ:BOA:taz:'

devices = dict(
    taz = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'TAZ translation',
        motorpv = pvprefix + 'TAZ',
        errormsgpv = pvprefix + 'TAZ-MsgTxt',
        precision = 0.00055
    ),
)
