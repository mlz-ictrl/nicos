description = 'Setup for the standard sample table'

pvprefix = 'SQ:SANS-LLB:turboPmac1:'

devices = dict(
    stom = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        epicstimeout = 3.0,
        description = 'Sample table rotation around Y',
        motorpv = pvprefix + 'stom',
    ),
    stx = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        epicstimeout = 3.0,
        description = 'Sample table translation along X',
        motorpv = pvprefix + 'stx',
    ),
    stz = device('nicos.devices.generic.manual.ManualMove',
        description = 'Sample table Z (along the beam, fixed)',
        unit = 'mm',
        abslimits = (0, 170)
    ),
    stgn = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        epicstimeout = 3.0,
        description = 'Sample table goniometer (rotation around X)',
        motorpv = pvprefix + 'stgn',
    ),
    sty = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        epicstimeout = 3.0,
        description = 'Sample table translation along Y',
        motorpv = pvprefix + 'sty',
    ),
    spos = device('nicos_sinq.devices.epics.sinqmotor_deprecated.SinqMotor',
        epicstimeout = 3.0,
        description = 'Sample chnager position',
        motorpv = pvprefix + 'spos',
    ),
)
