description = 'BOA rotation table 2'

pvprefix = 'SQ:BOA:drot2:'

devices = dict(
    rd = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Rotation table 2 bottom motor',
        motorpv = pvprefix + 'RD',
        errormsgpv = pvprefix + 'RB-MsgTxt',
    ),
    re = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Rotation table 2 top motor',
        motorpv = pvprefix + 'RE',
        errormsgpv = pvprefix + 'RE-MsgTxt',
    ),
    rcu = device('nicos_sinq.boa.devices.counterrotation.CounterRotatingMotor',
        description = 'Rotation Table 2 upper counter rotation',
        master = 'rd',
        slave = 're',
        unit = 'mm',
        target = 0,
    ),
    rcl = device('nicos_sinq.boa.devices.counterrotation.CounterRotatingMotor',
        description = 'Rotation Table 1 lowercounter rotation',
        master = 're',
        slave = 'rd',
        unit = 'mm',
        target = 0,
    ),
)
