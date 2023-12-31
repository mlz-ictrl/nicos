description = 'system setup'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'TEST',
    experiment = 'Exp',
    datasinks = ['conssink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    TEST = device('nicos.devices.instrument.Instrument',
        description = 'Instrument object',
        instrument = 'TEST',
        responsible = 'g.brandl@fz-juelich.de',
        website = 'https://www.nicos-controls.org',
        facility = 'Forschungszentrum Jülich',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'No sample',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/data',
        sample = 'Sample',
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
