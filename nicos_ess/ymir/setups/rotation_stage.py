description = 'Stray motion stage(s) at YMIR.'

pv_root = 'SES-SCAN:MC-MCU-001:'
devices = dict(
    rotation_stage=device('nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='Rotation stage in YMIR',
        motorpv=f'{pv_root}m4',
        errormsgpv=f'{pv_root}m4-MsgTxt',
        errorbitpv=f'{pv_root}m4-Err',
        reseterrorpv=f'{pv_root}m4-ErrRst',
        monitor=True,
    ),
)
