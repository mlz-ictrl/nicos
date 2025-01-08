description = 'CAMEA basic devices: motors, counters and such'

display_order = 40

pvmcu1 = 'SQ:CAMEA:mcu1:'
pvmcu2 = 'SQ:CAMEA:mcu2:'
pvmcu3 = 'SQ:CAMEA:mcu3:'
pvmcu4 = 'SQ:CAMEA:mcu4:'

devices = dict(
    gl = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Sample table lower goniometer',
        motorpv = pvmcu1 + 'gl',
        errormsgpv = pvmcu1 + 'gl-MsgTxt',
        precision = 0.02,
        can_disable = True,
    ),
    gu = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Sample table upper goniometer',
        motorpv = pvmcu1 + 'gu',
        errormsgpv = pvmcu1 + 'gu-MsgTxt',
        precision = 0.02,
        can_disable = True,
    ),
    tl = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Sample table lower translation',
        motorpv = pvmcu1 + 'tl',
        errormsgpv = pvmcu1 + 'tl-MsgTxt',
        precision = 0.02,
        can_disable = True,
    ),
    tu = device('nicos_sinq.devices.epics.motor_deprecated.EpicsMotor',
        description = 'Sample table upper translation',
        motorpv = pvmcu1 + 'tu',
        errormsgpv = pvmcu1 + 'tu-MsgTxt',
        precision = 0.02,
        can_disable = True,
    ),
)
startupcode = """
sgl.alias = 'gl'
sgu.alias = 'gu'
"""
