description = 'BOA Chopper'

pvprefix = 'SQ:BOA:mcu3:'

devices = dict(
    ch1 = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Chopper 1 Motor',
        motorpv = pvprefix + 'CH1',
        errormsgpv = pvprefix + 'CH1-MsgTxt',
        can_disable = True,
    ),
    ch2 = device('nicos_sinq.devices.epics.motor.EpicsMotor',
        description = 'Chopper 2 Motor',
        motorpv = pvprefix + 'CH2',
        errormsgpv = pvprefix + 'CH2-MsgTxt',
        can_disable = True,
    ),
)
