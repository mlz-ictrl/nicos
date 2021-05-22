description = 'AMOR unpolarized deflected beam mode'

group = 'basic'

pvprefix = 'SQ:AMOR:motc:'

devices = dict(
    ltz = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Deflector vertical translation',
        motorpv = pvprefix + 'ltz',
        errormsgpv = pvprefix + 'ltz-MsgTxt',
    ),
    lom = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Deflector tilt',
        motorpv = pvprefix + 'lom',
        errormsgpv = pvprefix + 'lom-MsgTxt',
    ),
)

startupcode = '''
Exp.mode = 'deflector'
'''
