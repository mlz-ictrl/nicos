#  -*- coding: utf-8 -*-

description = 'system setup'

sysconfig = dict(
    cache = 'antareshw.antares.frm2',
    instrument = 'ANTARES',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['commands.basic', 'commands.standard', 'antares.commands']

includes = ['notifiers']

devices = dict(
    Sample = device('devices.experiment.Sample',
        description = 'Default Sample',
    ),
    Exp = device('antares.experiment.Experiment',
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
    ANTARES = device('devices.instrument.Instrument',
        description = 'Antares Instrument',
        instrument = 'ANTARES',
        responsible = 'Michael Schulz <michael.schulz@frm2.tum.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-42',
    ),
    filesink = device('devices.datasinks.AsciiScanfileSink',
        description = 'Scanfile storing device',
    ),
    conssink = device('devices.datasinks.ConsoleScanSink',
        description = 'Device handling console output',
    ),
    daemonsink = device('devices.datasinks.DaemonSink',
        description = 'Data handling inside the daemon',
    ),
    Space = device('devices.generic.FreeSpace',
        description = 'Free Space in the RootDir of AntaresHW',
        path = '/',
        minfree = 5,
    ),
    DataSpace = device('devices.generic.FreeSpace',
        description = 'Free Space on the DataStorage',
        path = '/data',
        minfree = 500,
    ),
)
