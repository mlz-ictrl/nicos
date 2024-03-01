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

startupcode = '''
SetDetectors(adet)
ClearSamples()
SetSample(1, 'Absorbtion experiment FoPra', sampletype=1)
SetSample(2, 'Strain experiment FoPra E-Mod 211', sampletype=2)
SetSample(3, 'Strain experiment FoPra E-Mod 200', sampletype=3)
SetSample(4, 'fully flexible sample', sampletype=4)
SelectSample(1)
'''
