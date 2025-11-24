description = 'The motor for controlling the camera position'

devices = dict(
    camera_box_motor=device(
        'nicos_ess.devices.epics.pva.motor.EpicsMotor',
        description='The camera box motor',
        motorpv='YMIR-4004:MC-MCU-02:Mtr4',
        pollinterval=0.5,
        maxage=None,
        monitor=True,
        pva=True,
    ),
    brake=device(
        'nicos.devices.epics.EpicsMappedMoveable',
        description='The brake for the camera box motor',
        readpv='YMIR-4004:MC-MCU-02:Mtr4-ReleaseBrake',
        writepv='YMIR-4004:MC-MCU-02:Mtr4-ReleaseBrake',
        pva=True,
        monitor=True,
        pollinterval=0.5,
        maxage=None,
    )
)
