description = 'BOA Goniometer G'

pvprefix = 'SQ:BOA:dg:'

devices = dict(
    gau = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Goniometer G upper',
        motorpv = pvprefix + 'GAU',
        errormsgpv = pvprefix + 'GAU-MsgTxt',
    ),
    gal = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Goniometer G lower',
        motorpv = pvprefix + 'GAL',
        errormsgpv = pvprefix + 'GAL-MsgTxt',
    ),
)
