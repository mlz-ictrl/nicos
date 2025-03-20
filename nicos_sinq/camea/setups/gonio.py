description = 'CAMEA basic devices: motors, counters and such'

display_order = 40

pvmcu1 = 'SQ:CAMEA:turboPmac1:'
pvmcu2 = 'SQ:CAMEA:turboPmac2:'
pvmcu3 = 'SQ:CAMEA:turboPmac3:'
pvmcu4 = 'SQ:CAMEA:turboPmac4:'

devices = dict(
    gl = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample table lower goniometer',
        motorpv = pvmcu1 + 'gl',
    ),
    gu = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample table upper goniometer',
        motorpv = pvmcu1 + 'gu',
    ),
    tl = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample table lower translation',
        motorpv = pvmcu1 + 'tl',
    ),
    tu = device('nicos_sinq.devices.epics.motor.SinqMotor',
        description = 'Sample table upper translation',
        motorpv = pvmcu1 + 'tu',
    ),
)
startupcode = """
sgl.alias = 'gl'
sgu.alias = 'gu'
"""
