description = 'BOA Adaptive Obtics Setup'

pvprefix = 'SQ:BOA:adap:'

devices = dict(
    paw = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Motor PAW',
        motorpv = pvprefix + 'PAW',
        errormsgpv = pvprefix + 'PAW-MsgTxt',
        precision = 1
    ),
    paa = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Motor PAA',
        motorpv = pvprefix + 'PAA',
        errormsgpv = pvprefix + 'PAA-MsgTxt',
        precision = 1
    ),
    pbw = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Motor PBW',
        motorpv = pvprefix + 'PBW',
        errormsgpv = pvprefix + 'PBW-MsgTxt',
        precision = 1
    ),
    pba = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Motor PBA',
        motorpv = pvprefix + 'PBA',
        errormsgpv = pvprefix + 'PBA-MsgTxt',
        precision = 1
    ),
)
