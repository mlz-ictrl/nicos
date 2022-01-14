description = 'BOA Adaptive Obtics Setup'

pvprefix = 'SQ:BOA:adap:'

devices = dict(
    paw = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Motor PAW',
        motorpv = pvprefix + 'PAW',
        errormsgpv = pvprefix + 'PAW-MsgTxt',
    ),
    paa = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Motor PAA',
        motorpv = pvprefix + 'PAA',
        errormsgpv = pvprefix + 'PAA-MsgTxt',
    ),
    pbw = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Motor PBW',
        motorpv = pvprefix + 'PBW',
        errormsgpv = pvprefix + 'PBW-MsgTxt',
    ),
    pba = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Motor PBA',
        motorpv = pvprefix + 'PBA',
        errormsgpv = pvprefix + 'PBA-MsgTxt',
    ),
)
