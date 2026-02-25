devices = dict(
    motor1 = device('test.utils.FakeEpicsMotor',
        unit = 'mm',
        motorpv = 'IOC:m1',
    ),
    motor2 = device('test.utils.DerivedEpicsMotor',
        unit = 'mm',
        motorpv = 'IOC:m2',
    ),
)
