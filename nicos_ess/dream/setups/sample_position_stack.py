description = 'The sample alignment stack for DREAM'
prefix = "IOC"

devices = dict(
    pos_x=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        unit='mm',
        precision=0.1,
        description='X axis alignment',
        motorpv=f'{prefix}:m1',
        monitor=True,
    ),
    pos_y=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        unit='mm',
        precision=0.1,
        description='Y axis alignment',
        motorpv=f'{prefix}:m2',
        monitor=True,
    ),
    pos_z=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        unit='mm',
        precision=0.1,
        description='Z axis alignment',
        motorpv=f'{prefix}:m3',
        monitor=True,
    ),
)
