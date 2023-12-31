description = 'system setup'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost:14870',
    instrument = 'jcnsmon',
    experiment = 'Exp',
    datasinks = ['conssink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    jcnsmon = device('nicos.devices.instrument.Instrument',
        description = 'JCNS monitoring infrastructure',
        instrument = 'JCNSmon',
        responsible = 'G. Brandl <g.brandl@fz-juelich.de>',
        operators = ['Jülich Centre for Neutron Science (JCNS)'],
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
