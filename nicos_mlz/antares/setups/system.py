#  -*- coding: utf-8 -*-

description = 'system setup'

sysconfig = dict(
    cache = 'antareshw.antares.frm2',
    instrument = 'ANTARES',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.basic', 'nicos.commands.standard',
           'nicos_mlz.antares.commands']

includes = ['notifiers']

devices = dict(
    Sample = device('nicos.devices.experiment.Sample',
        description = 'Default Sample',
    ),
    Exp = device('nicos_mlz.antares.devices.experiment.Experiment',
        description = 'Antares Experiment',
        dataroot = '/data/FRM-II',
        sample = 'Sample',
        propdb = '/etc/propdb',
        mailsender = 'antares@frm2.tum.de',
        propprefix = 'p',
        serviceexp = 'service',
        servicescript = '',
        templates = 'templates',
        sendmail = False,
        zipdata = False,
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o775,
            disableFileMode = 0o664,
        ),
    ),
    ANTARES = device('nicos.devices.instrument.Instrument',
        description = 'Antares Instrument',
        instrument = 'ANTARES',
        responsible = 'Michael Schulz <michael.schulz@frm2.tum.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-42',
        operators = [u'Technische Universität München (TUM)'],
        website = 'http://www.mlz-garching.de/antares',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        description = 'Scanfile storing device',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        description = 'Device handling console output',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        description = 'Data handling inside the daemon',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'Free Space in the RootDir of AntaresHW',
        path = '/',
        minfree = 5,
    ),
    DataSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free Space on the DataStorage',
        path = '/data',
        minfree = 500,
    ),
)
