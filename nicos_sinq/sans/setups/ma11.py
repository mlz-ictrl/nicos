description = 'Setup for the ma11 dom motor'

devices = dict(
    dom = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Sample stick rotation',
        motorpv = 'SQ:SANS:ma11:dom',
        errormsgpv = 'SQ:SANS:ma11:dom-MsgTxt',
        precision = 0.1,
    ),
)
