description = 'Stray motion stage(s) at YMIR.'

pv_root = 'YMIR-SpRot:MC-Rz-01:'
devices = dict(rotation_stage=device(
    'nicos_ess.devices.epics.pva.motor.EpicsMotor',
    description='Rotation stage in YMIR',
    motorpv=f'{pv_root}m',
    powerautopv=f'{pv_root}m-PwrAuto',
    errormsgpv=f'{pv_root}m-MsgTxt',
    errorbitpv=f'{pv_root}m-Err',
    reseterrorpv=f'{pv_root}m-ErrRst',
    pollinterval=None,
    monitor=True,
    pva=True,
), )
