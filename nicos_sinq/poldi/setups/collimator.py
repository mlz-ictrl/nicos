description = 'POLDI collimator'

pvpref = 'SQ:POLDI:MCU2:'

devices = dict(
    cr1 = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Collimator rotational stage',
        motorpv = pvpref + 'CR1',
        precision = 0.01,
    ),
    ctl1 = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Collimator Y translation stage',
        motorpv = pvpref + 'CTL1',
        precision = 0.001,
    ),
    ctu1 = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Collimator X translation stage',
        motorpv = pvpref + 'CTU1',
        precision = 0.001,
    ),
)
