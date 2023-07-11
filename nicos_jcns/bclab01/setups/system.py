description = 'system setup'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'bclab',
    experiment = 'Exp',
    datasinks = ['conssink', 'daemonsink'],
    notifiers = ['email'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    bclab = device('nicos.devices.instrument.Instrument',
        description = 'Bio/chemistry lab NICOS setup',
        instrument = 'bclab',
        responsible = 'T. Schrader <t.schrader@fz-juelich.de>',
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
