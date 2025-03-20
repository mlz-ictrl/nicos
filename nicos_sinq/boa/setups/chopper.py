description = 'BOA Chopper'

pvprefix = 'SQ:BOA:turboPmac3:'

devices = dict(
    ch1 = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Chopper 1 Motor',
        motorpv = pvprefix + 'CH1',
    ),
    ch2 = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Chopper 2 Motor',
        motorpv = pvprefix + 'CH2',
        errormsgpv = pvprefix + 'CH2-MsgTxt',
        can_disable = True,
    ),
)
