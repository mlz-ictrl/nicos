description = 'system setup'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Instrument = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'ictrl',
        responsible = 'Jens Krüger <jens.krueger@frm2.tum.de>',
        operators = ['Technische Universität München (TUM)'],
        website = 'http://www.mlz-garching.de/',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = 'data',
        serviceexp = 'p0',
        sample = 'Sample',
        managerights = dict(
            owner = 'nicd',
            group = 'ictrl',
            enableDirMode = 0o750,
            enableFileMode = 0o640,
            disableDirMode = 0o550,
            disableFileMode = 0o440,
        ),
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
