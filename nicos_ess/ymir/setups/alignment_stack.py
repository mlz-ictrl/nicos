description = 'The motion stages for alignment in the YMIR cave'

devices = dict(
    mX=device(
        'nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout=3.0,
        precision=0.1,
        description='Single axis positioner',
        motorpv='SES-SCAN:MC-MCU-001:m1',
        errormsgpv='SES-SCAN:MC-MCU-001:m1-MsgTxt',
        errorbitpv='SES-SCAN:MC-MCU-001:m1-Err',
        reseterrorpv='SES-SCAN:MC-MCU-001:m1-ErrRst',
    ),
    mY=device(
        'nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout=3.0,
        precision=0.1,
        description='Single axis positioner',
        motorpv='SES-SCAN:MC-MCU-001:m2',
        errormsgpv='SES-SCAN:MC-MCU-001:m2-MsgTxt',
        errorbitpv='SES-SCAN:MC-MCU-001:m2-Err',
        reseterrorpv='SES-SCAN:MC-MCU-001:m2-ErrRst',
    ),
    mZ=device(
        'nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout=3.0,
        precision=0.1,
        description='Single axis positioner',
        motorpv='SES-SCAN:MC-MCU-001:m3',
        errormsgpv='SES-SCAN:MC-MCU-001:m3-MsgTxt',
        errorbitpv='SES-SCAN:MC-MCU-001:m3-Err',
        reseterrorpv='SES-SCAN:MC-MCU-001:m3-ErrRst',
    ),
)
