description = 'BOA rotation table 1'

pvprefix = 'SQ:BOA:drot1:'

devices = dict(
    rb = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Rotation table 1 bottom motor',
        motorpv = pvprefix + 'RB',
        errormsgpv = pvprefix + 'RB-MsgTxt',
        precision = 0.0001
    ),
    rc = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Rotation table 1 top motor',
        motorpv = pvprefix + 'RC',
        errormsgpv = pvprefix + 'RC-MsgTxt',
        precision = 0.0001
    ),
    rbu = device('nicos_sinq.boa.devices.counterrotation.CounterRotatingMotor',
        description = 'Rotation Table 1 upper counter rotation',
        master = 'rb',
        slave = 'rc',
        unit = 'mm',
        target = 0,
    ),
    rbl = device('nicos_sinq.boa.devices.counterrotation.CounterRotatingMotor',
        description = 'Rotation Table 1 lowercounter rotation',
        master = 'rc',
        slave = 'rb',
        unit = 'mm',
        target = 0,
    ),
)
