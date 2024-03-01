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

devices = dict(
    Sample = device('nicos_virt_mlz.stressi.devices.sample.Sample',
        description = 'Simulation sample',
        samples = {
            1: {'name': 'Absorbtion experiment FoPra', 'sampletype': 1},
            2: {'name': 'Strain experiment FoPra E-Mod 211', 'sampletype': 2},
            3: {'name': 'Strain experiment FoPra E-Mod 200', 'sampletype': 3},
            4: {'name': 'Fully flexible sample', 'sampletype': 4},
        },
    ),
)

startupcode = '''
SelectSample(1)
'''
