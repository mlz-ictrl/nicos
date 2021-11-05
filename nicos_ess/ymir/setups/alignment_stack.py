description = 'The motion stages for alignment in the YMIR cave'

devices = dict(
    mX=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='Single axis positioner',
        motorpv='SES-SCAN:MC-MCU-001:m1',
        errormsgpv='SES-SCAN:MC-MCU-001:m1-MsgTxt',
        errorbitpv='SES-SCAN:MC-MCU-001:m1-Err',
        reseterrorpv='SES-SCAN:MC-MCU-001:m1-ErrRst',
        monitor=True,
    ),
    mY=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='Single axis positioner',
        motorpv='SES-SCAN:MC-MCU-001:m2',
        errormsgpv='SES-SCAN:MC-MCU-001:m2-MsgTxt',
        errorbitpv='SES-SCAN:MC-MCU-001:m2-Err',
        reseterrorpv='SES-SCAN:MC-MCU-001:m2-ErrRst',
        monitor=True,
    ),
    mZ=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='Single axis positioner',
        motorpv='SES-SCAN:MC-MCU-001:m3',
        errormsgpv='SES-SCAN:MC-MCU-001:m3-MsgTxt',
        errorbitpv='SES-SCAN:MC-MCU-001:m3-Err',
        reseterrorpv='SES-SCAN:MC-MCU-001:m3-ErrRst',
        monitor=True,
    ),
)
