description = 'Setup for the standard sample table'

pvprefix = 'SQ:SANS-LLB:mcu2:'

devices = dict(
    stx = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'Sample table X',
        motorpv = pvprefix + 'stx',
        errormsgpv = pvprefix + 'stx-MsgTxt',
        precision = 0.01,
    ),
    sty = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'Sample table Y',
        motorpv = pvprefix + 'sty',
        errormsgpv = pvprefix + 'sty-MsgTxt',
        precision = 0.01,
    ),
    stz = device('nicos.devices.generic.manual.ManualMove',
        description = 'Manually adjustable sample table z position',
        unit = 'mm',
        abslimits = (0, 170)
    ),
    stom = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'Sample table rotation',
        motorpv = pvprefix + 'stom',
        errormsgpv = pvprefix + 'stom-MsgTxt',
        precision = 0.01,
    ),
    stgn = device('nicos_ess.devices.epics.motor.HomingProtectedEpicsMotor',
        epicstimeout = 3.0,
        description = 'Sample table goniometer',
        motorpv = pvprefix + 'stgn',
        errormsgpv = pvprefix + 'stgn-MsgTxt',
        precision = 0.01,
    ),
)
