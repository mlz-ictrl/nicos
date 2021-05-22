description = 'Detector stage'

pvprefix = 'SQ:AMOR:motserial:'

devices = dict(
    com = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Detector tilt',
        motorpv = pvprefix + 'com',
        errormsgpv = pvprefix + 'com-MsgTxt',
    ),
    coz = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Detector height',
        motorpv = pvprefix + 'coz',
        errormsgpv = pvprefix + 'coz-MsgTxt',
    ),
    xc = device('nicos.devices.generic.VirtualMotor',
        description = 'Reference wrt the beam axis',
        abslimits = (0, 730),
        unit = 'mm',
        curvalue = 200
    ),
    xcOffset = device('nicos.devices.generic.VirtualMotor',
        description = 'Eventual extra offset due to interposed devices',
        abslimits = (0, 730),
        unit = 'mm',
        curvalue = 500
    ),
)
