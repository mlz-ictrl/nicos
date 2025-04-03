description = 'POLDI collimator'

pvpref = 'SQ:POLDI:turboPmac2:'

devices = dict(
    cr1 = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Collimator rotational stage',
        motorpv = pvpref + 'CR1',
    ),
    ctl1 = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Collimator Y translation stage',
        motorpv = pvpref + 'CTL1',
    ),
    ctu1 = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Collimator X translation stage',
        motorpv = pvpref + 'CTU1',
    ),
)
