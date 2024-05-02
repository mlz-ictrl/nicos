description = 'STRESS-SPEC setup with sample table'

group = 'basic'

includes = [
    'standard',
    'sampletable',
]

sysconfig = dict(
    datasinks = ['caresssink'],
)

devices = dict(
    Sample = device('nicos_virt_mlz.stressi.devices.sample.Sample',
        description = 'Simulation sample',
        samples = {
            1: {'name': 'Absorption experiment FoPra', 'sampletype': 1},
            2: {'name': 'Strain experiment FoPra E-Mod 211', 'sampletype': 2},
            3: {'name': 'Strain experiment FoPra E-Mod 200', 'sampletype': 3},
            4: {'name': 'Fully flexible sample', 'sampletype': 4},
        },
    ),
)

startupcode = '''
SelectSample(1)
'''
