description = 'AMOR unpolarized deflected beam mode'

group = 'basic'

pvprefix = 'SQ:AMOR:motc:'

devices = dict(
    ltz = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Deflector vertical translation',
        motorpv = pvprefix + 'ltz',
        errormsgpv = pvprefix + 'ltz-MsgTxt',
    ),
    lom = device('nicos.devices.epics.pyepics.motor.EpicsMotor',
        description = 'Deflector tilt',
        motorpv = pvprefix + 'lom',
        errormsgpv = pvprefix + 'lom-MsgTxt',
    ),
)

startupcode = '''
Exp.mode = 'deflector'
'''
