description = 'BOA Goniometer GBL'

pvprefix = 'SQ:BOA:gbl:'

devices = dict(
    gbl = device('nicos_ess.devices.epics.motor.EpicsMotor',
        description = 'Goniometer GBL',
        motorpv = pvprefix + 'GBL',
        errormsgpv = pvprefix + 'GBL-MsgTxt',
    ),
)
