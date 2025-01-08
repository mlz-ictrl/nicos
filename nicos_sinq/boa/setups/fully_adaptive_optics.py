description = 'BOA Adaptive Obtics Setup'

pvprefix = 'SQ:BOA:adap:'

devices = dict(
    paw = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Motor PAW',
        motorpv = pvprefix + 'PAW',
        errormsgpv = pvprefix + 'PAW-MsgTxt',
    ),
    paa = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Motor PAA',
        motorpv = pvprefix + 'PAA',
        errormsgpv = pvprefix + 'PAA-MsgTxt',
    ),
    pbw = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Motor PBW',
        motorpv = pvprefix + 'PBW',
        errormsgpv = pvprefix + 'PBW-MsgTxt',
    ),
    pba = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Motor PBA',
        motorpv = pvprefix + 'PBA',
        errormsgpv = pvprefix + 'PBA-MsgTxt',
    ),
)
