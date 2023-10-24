description = 'The motors for alignment in the YMIR cave'

devices = dict(
    mX=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='Single axis positioner',
        motorpv='YMIR-SpScn:MC-X-01:Mtr',
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
    mY=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='Single axis positioner',
        motorpv='YMIR-SpScn:MC-Y-01:Mtr',
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
    mZ=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='Single axis positioner',
        motorpv='YMIR-SpScn:MC-Z-01:Mtr',
        pollinterval=None,
        monitor=True,
        pva=True,
    ),
)
