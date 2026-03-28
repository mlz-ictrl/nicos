description = 'Test setup for motor deprecated'

devices = dict(
 bsx = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Beamstop Y Translation',
        motorpv = 'SQ:SINQTEST:el734_1:bsx',
        errormsgpv = 'SQ:SINQTEST:el734_1:bsx-MsgTxt',
        precision = 0.2
    ),
)
