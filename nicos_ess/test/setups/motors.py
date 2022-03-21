devices = dict(
    motor1 = device('test.utils.FakeEpicsMotor',
        unit = 'mm',
        motorpv = 'IOC:m1',
        abslimits=(-110, 110),
    ),
    motor2 = device('test.utils.DerivedEpicsMotor',
        unit = 'mm',
        motorpv = 'IOC:m2',
        abslimits=(-120, 120),
    ),
)
