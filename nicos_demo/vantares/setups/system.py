#  -*- coding: utf-8 -*-

description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'ANTARES',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = ['nicos.commands.basic', 'nicos.commands.standard',
           'nicos_mlz.antares.commands']

devices = dict(
    Sample = device('nicos.devices.experiment.Sample',
        description = 'Default Sample',
    ),
    Exp = device('nicos_mlz.antares.devices.Experiment',
        description = 'Antares Experiment',
        dataroot = 'data/FRM-II',
        sample = 'Sample',
        propprefix = 'p',
        serviceexp = 'service',
        servicescript = '',
        templates = 'templates',
        sendmail = False,
        zipdata = False,
        managerights = dict(
            enableDirMode = 0o770,
            enableFileMode = 0o660,
            disableDirMode = 0o550,
            disableFileMode = 0o440,
        ),
    ),
    ANTARES = device('nicos.devices.instrument.Instrument',
        description = 'Antares Instrument',
        instrument = 'ANTARES',
        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-42',
        operators = ['NICOS developer team'],
        website = 'http://www.mlz-garching.de/antares',
        facility = 'NICOS demo instruments',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        filemode=0o440,
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    DataSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free Space on the DataStorage',
        path = 'data',
        minfree = 100,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free space on the log drive',
        path = 'log',
        visibility = (),
        warnlimits = (0.5, None),
    ),
)
