description = 'BOA Goniometer GBL'

pvprefix = 'SQ:BOA:gbl:'

devices = dict(
    gbl = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Goniometer GBL',
        motorpv = pvprefix + 'GBL',
        errormsgpv = pvprefix + 'GBL-MsgTxt',
    ),
)
