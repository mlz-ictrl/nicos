description = 'system setup'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'resist',
    experiment = 'Exp',
    datasinks = ['conssink', 'daemonsink', 'asciisink'],
    notifiers = ['email'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers', 'lakeshore']

devices = dict(
    resist = device('nicos.devices.instrument.Instrument',
        description = 'Sample prep lab resistivity setup',
        instrument = 'resist',
        responsible = 'Yixi Su <y.su@fz-juelich.de>',
        operators = ['Jülich Centre for Neutron Science (JCNS)'],
        visibility = {'metadata'},
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
    asciisink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
)
