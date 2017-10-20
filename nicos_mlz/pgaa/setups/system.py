description = 'system setup'

sysconfig = dict(
    cache = 'tequila.pgaa.frm2',
    instrument = 'PGAA',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

group = 'lowlevel'

includes = ['notifiers']

devices = dict(
    Sample = device('nicos.devices.sample.Sample',
        description = 'The sample',
    ),

    PGAA = device('nicos.devices.instrument.Instrument',
        description = 'Prompt gamma and in-beam neutron activation analysis '
                      'facility',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-46',
        responsible = 'Dr. Zsolt Revay <zsolt.revay@frm2.tum.de>',
    ),

    Exp = device('nicos.devices.experiment.Experiment',
        description = 'The currently running experiment',
        dataroot = '/localdata/',
        sample = 'Sample',
    ),

    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        lowlevel = True,
    ),

    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        lowlevel = True,
    ),

    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        lowlevel = True,
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        minfree = 5,
    ),
)
