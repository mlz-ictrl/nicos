description = 'The motors for alignment in the YMIR cave'

pv_root = 'SES-SCAN:MC-MCU-001:'
devices = dict(
    mX=device('nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='Single axis positioner',
        motorpv=f'{pv_root}m1',
        errormsgpv=f'{pv_root}m1-MsgTxt',
        errorbitpv=f'{pv_root}m1-Err',
        reseterrorpv=f'{pv_root}m1-ErrRst',
        monitor=True,
    ),
    mY=device('nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='Single axis positioner',
        motorpv=f'{pv_root}m2',
        errormsgpv=f'{pv_root}m2-MsgTxt',
        errorbitpv=f'{pv_root}m2-Err',
        reseterrorpv=f'{pv_root}m2-ErrRst',
        monitor=True,
    ),
    mZ=device('nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='Single axis positioner',
        motorpv=f'{pv_root}m3',
        errormsgpv=f'{pv_root}m3-MsgTxt',
        errorbitpv=f'{pv_root}m3-Err',
        reseterrorpv=f'{pv_root}m3-ErrRst',
        monitor=True,
    ),
)
