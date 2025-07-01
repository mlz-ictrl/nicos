description = 'Virtual STRESS-SPEC instrument'

group = 'basic'

includes = [
    'standard', 'sampletable', 'eulerian',
]

sysconfig = dict(
    datasinks = ['caresssink'],
)

devices = dict(
    m1_foc = device('nicos.devices.generic.VirtualMotor',
        description = 'M1_FOC',
        fmtstr = '%.2f',
        unit = 'steps',
        abslimits = (0, 4096),
        speed = 10,
    ),
    m3_foc = device('nicos.devices.generic.VirtualMotor',
        description = 'M3_FOC',
        fmtstr = '%.2f',
        unit = 'steps',
        abslimits = (0, 4096),
        speed = 10,
    ),
)

startupcode = """
SetDetectors(adet)
SelectSample(1)
"""
