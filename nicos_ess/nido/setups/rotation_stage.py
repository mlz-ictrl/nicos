description = 'Rotation stage'

pv_root = 'YMIR-4004:MC-Rz-01:'

devices = dict(rotation_stage=device(
    'nicos_ess.devices.epics.pva.motor.EpicsMotor',
    description='Rotation stage',
    motorpv=f'{pv_root}m',
    pollinterval=None,
    monitor=True,
    pva=True,
), )
