description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'hrpd',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email'],
)

modules = ['nicos.commands.standard']

includes = [
    'notifiers',
]

devices = dict(
    hrpd = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'HRPD',
        responsible = 'rifai <rifai@batan.go.id>',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),

    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = 'data',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
)
