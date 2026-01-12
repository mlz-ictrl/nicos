description = 'TOFTOF basic instrument setup'

group = 'basic'

includes = [
    'vdetector',
    'vchopper',
    'vacuum',
    'voltage',
    'safety',
    'reactor',
    'nl2a',
    'table',
    'slit',
    'collimator',
    'rc',
    'samplememograph',
    'chiller',
]

sysconfig = dict(
    experiment = 'Exp',
)

devices = dict(
    Sample = device('nicos_virt_mlz.toftof.devices.sample.Sample',
        description = 'The currently used sample',
        samples = {
            1: {'name': 'Vanadium', 'sampletype': 0, 'nature': 'powder'},
            2: {'name': 'Empty can', 'sampletype': 1, 'type': 'can',},
            3: {'name': 'Water', 'sampletype': 2, 'type': 'sample+can',
                'nature': 'liquid'},
        },
    ),
    Exp = device('nicos_mlz.toftof.devices.Experiment',
        description = 'The currently running experiment',
        propprefix = '',
        dataroot = '/data',  # configdata('config_data.dataroot'),
        sendmail = True,
        serviceexp = 'p0',
        sample = 'Sample',
        reporttemplate = '',
        elog = True,
        forcescandata = True,
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o550,
            disableFileMode = 0o440,
            owner = 'toftof',
            group = 'toftof',
        ),
        counterfile = 'counter',
    ),
)

startupcode = '''
SetDetectors(det)
'''
