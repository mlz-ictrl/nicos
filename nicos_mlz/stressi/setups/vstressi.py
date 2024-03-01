description = 'STRESS-SPEC setup with sample table'

group = 'basic'

includes = [
    'system',
    'reactor',
    'monochromator',
    'slits',
    'primaryslit',
    'sampletable',
    'vdetector',
]

sysconfig = dict(
    datasinks = ['caresssink'],
)

startupcode = '''
ClearSamples()
SetSample(1, 'Absorbtion experiment FoPra', sampletype=1)
SetSample(2, 'Strain experiment FoPra E-Mod 211', sampletype=2)
SetSample(3, 'Strain experiment FoPra E-Mod 200', sampletype=3)
SetSample(4, 'fully flexible sample', sampletype=4)
SelectSample(1)
'''
