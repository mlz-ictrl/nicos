description = 'system setup'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'MOKE',
    experiment = 'Exp',
    datasinks = ['conssink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    MOKE = device('nicos.devices.instrument.Instrument',
        description = 'MOKE setup',
        instrument = 'MOKE',
        responsible = 'S. Pütter <s.puetter@fz-juelich.de>',
        operators = ['Jülich Centre for Neutron Science (JCNS)'],
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'No sample',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/data',
        sendmail = False,
        serviceexp = 'service',
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
