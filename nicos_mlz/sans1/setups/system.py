description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'ctrl.sans1.frm2.tum.de',
    instrument = 'Instrument',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'nxsink'],
    notifiers = ['email'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Sample = device('nicos_mlz.sans1.devices.sample.Sample',
        description = 'sample',
    ),
    Instrument = device('nicos.devices.instrument.Instrument',
        description = 'SANS1 instrument',
        instrument = 'SANS-1',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-32',
        responsible = 'Dr. Andre Heinemann <Andre.Heinemann@hzg.de>',
        operators = ['German Engineering Materials Science Centre (GEMS)',
                     'Technische Universität München (TUM)',
                    ],
        website = 'http://www.mlz-garching.de/sans-1',
    ),
    Exp = device('nicos_mlz.devices.experiment.Experiment',
        description = 'experiment',
        dataroot = '/data/nicos',
        sample = 'Sample',
        sendmail = True,
        mailsender = 'sans1@frm2.tum.de',
        managerights = dict(
            enableDirMode = 0o777,
            enableFileMode = 0o666,
            disableDirMode = 0o750,
            disableFileMode = 0o640,
            owner = 'nicd',
            group = 'sans1'
        ),
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        description = 'filesink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        description = 'conssink',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        description = 'daemonsink',
    ),
    nxsink = device('nicos.nexus.NexusSink',
        templateclass = 'nicos_mlz.sans1.nexus.nexus_templates.SANSTemplateProvider',
        settypes = {'scan', 'point', 'subscan'},
        filenametemplate = ['%(scancounter)07d.nxs'],
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        minfree = 0.5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free space on the log drive',
        path = '/control/log',
        visibility = (),
        warnlimits = (0.5, None),
    ),
)
