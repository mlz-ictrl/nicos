description = 'BOA Chopper'

pvprefix = 'SQ:BOA:mcu3:'

devices = dict(
    ch1 = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Chopper 1 Motor',
        motorpv = pvprefix + 'CH1',
        errormsgpv = pvprefix + 'CH1-MsgTxt',
    ),
    ch2 = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Chopper 2 Motor',
        motorpv = pvprefix + 'CH2',
        errormsgpv = pvprefix + 'CH2-MsgTxt',
    ),
)
