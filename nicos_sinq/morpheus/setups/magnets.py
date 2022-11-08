description = 'Setup for the magnets at NARZISS'

pvprefix = 'SQ:MORPHEUS:'
motorpv = 'SQ:MORPHEUS:motb:'

devices = dict(
    afc = device('nicos_sinq.devices.epics.generic.EpicsAnalogMoveable',
        epicstimeout = 3.0,
        description = 'Analayzer magnet',
        readpv = pvprefix + 'AFC:CurRBV',
        writepv = pvprefix + 'AFC:CurSet',
        abslimits = (-5., 5.)
    ),
    pfc = device('nicos_sinq.devices.epics.generic.EpicsAnalogMoveable',
        epicstimeout = 3.0,
        description = 'Polarizer magnet',
        readpv = pvprefix + 'PFC:CurRBV',
        writepv = pvprefix + 'PFC:CurSet',
        abslimits = (-2.5, 2.5)
    ),
    pff = device('nicos_sinq.devices.epics.generic.EpicsAnalogMoveable',
        epicstimeout = 3.0,
        description = 'Polarizer magnet',
        readpv = pvprefix + 'PFF:CurRBV',
        writepv = pvprefix + 'PFF:CurSet',
        abslimits = (-2.5, 2.5)
    ),
    sbz = device('nicos_sinq.devices.epics.generic.EpicsAnalogMoveable',
        epicstimeout = 3.0,
        description = 'Sample magnet',
        readpv = pvprefix + 'SBZ:CurRBV',
        writepv = pvprefix + 'SBZ:CurSet',
        abslimits = (-80., 80.),
    ),
    pol = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Polarizer rotation',
        motorpv = motorpv + 'po1',
        precision = .1,
        errormsgpv = motorpv + 'po1-MsgTxt',
    ),
    ana = device('nicos_ess.devices.epics.motor.EpicsMotor',
        epicstimeout = 3.0,
        description = 'Analyzer rotation',
        motorpv = motorpv + 'po2',
        precision = .1,
        errormsgpv = motorpv + 'po2-MsgTxt',
    ),

