description = 'Detector stage'

display_order = 75

pvprefix = 'SQ:AMOR:mcu3:'

devices = dict(
    cnu = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Detector tilt',
        motorpv = pvprefix + 'com',
        errormsgpv = pvprefix + 'com-MsgTxt',
        unit = 'deg',
        precision = 0.001
    ),
    cz = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Detector height',
        motorpv = pvprefix + 'coz',
        errormsgpv = pvprefix + 'coz-MsgTxt',
        unit = 'mm',
        precision = 0.001
    ),
    det_park = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Detector parking motor',
        motorpv = pvprefix + 'park',
        errormsgpv = pvprefix + 'park-MsgTxt',
        abslimits = (-110, 10),
        precision = 0.001
    ),
    turmcontrol = device('nicos_sinq.amor.devices.turmcontrol.DetectorController',
        description = 'Prevent moving com and coz in park position',
        com = 'cnu',
        coz = 'cz',
        park = 'det_park',
        visibility = (),
    ),
    xc = device('nicos.devices.generic.VirtualMotor',
        description = 'Reference wrt the beam axis',
        abslimits = (0, 730),
        unit = 'mm',
        curvalue = 200,
        visibility = ('metadata', 'namespace'),
    ),
    xcOffset = device('nicos.devices.generic.VirtualMotor',
        description = 'Eventual extra offset due to interposed devices',
        abslimits = (0, 730),
        unit = 'mm',
        curvalue = 500,
        visibility = ('metadata', 'namespace'),
    ),
)
