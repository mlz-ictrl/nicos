description = 'STRESS-SPEC setup with sample table'

group = 'basic'

includes = [
    'vstandard',
    'sampletable',
    'sampletable_alias',
]

sysconfig = dict(
    datasinks = ['caresssink'],
)

tango_base = 'tango://motorbox06.stressi.frm2.tum.de:10000/box/'

devices = dict(
    Sample = device('nicos_virt_mlz.stressi.devices.Sample',
        description = 'Simulation sample',
        samples = {
            1: {
                'samplename': 'Sample 1',
                'sampledescription': 'Absorption experiment FoPra',
                'sampletype': 1,
                'lattice': [2.886, 2.886, 2.886],
                'angles': [90] * 3,
                'spacegroup': 'Im-3m',
                'density': 7.87,
                'formula': 'Fe',
                'mass': 1275,
                },
            2: {
                'samplename': 'Sample 2',
                'sampledescription': 'Strain experiment FoPra E-Mod 211',
                'sampletype': 2,
                'lattice': [2.886, 2.886, 2.886],
                'angles': [90] * 3,
                'spacegroup': 'Im-3m',
                'density': 7.87,
                'formula': 'Fe',
                'mass': 15.6,
                },
            3: {
                'samplename': 'Sample 3',
                'sampledescription': 'Strain experiment FoPra E-Mod 200',
                'sampletype': 3,
                'lattice': [2.886, 2.886, 2.886],
                'angles': [90] * 3,
                'spacegroup': 'Im-3m',
                'density': 7.87,
                'formula': 'Fe',
                'mass': 15.6,
                },
            # 4: {
            #     'samplename': 'Sample 4',
            #     'sampledescription': 'Fully flexible sample',
            #     'sampletype': 4,
            #     },
        },
    ),
    chis_m = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'channel1/motor',
        fmtstr = '%.2f',
        visibility = (),
    ),
    chis_c = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'channel1/coder',
        fmtstr = '%.2f',
        visibility = (),
    ),
    chis_v = device('nicos.devices.generic.Axis',
        description = 'Eulerian Huber CHIS',
        motor = 'chis_m',
        coder = 'chis_c',
        precision = 0.01,
    ),
    phis_m = device('nicos.devices.entangle.Motor',
        tangodevice = tango_base + 'channel2/motor',
        fmtstr = '%.2f',
        userlimits = (-700, 700),
        visibility = (),
    ),
    phis_c = device('nicos.devices.entangle.Sensor',
        tangodevice = tango_base + 'channel2/coder',
        fmtstr = '%.2f',
        visibility = (),
    ),
    phis_v = device('nicos.devices.generic.Axis',
        description = 'Eulerian Huber PHIS',
        motor = 'phis_m',
        coder = 'phis_c',
        precision = 0.01,
    ),
)

alias_config = {
    'phis': {'phis_v': 100,},
    'chis': {'chis_v': 100,},
}

startupcode = """
SelectSample(1)
"""
