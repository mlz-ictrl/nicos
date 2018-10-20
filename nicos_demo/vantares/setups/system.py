#  -*- coding: utf-8 -*-

description = 'system setup'

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
    Exp = device('nicos.devices.experiment.ImagingExperiment',
        description = 'Antares Experiment',
        dataroot = 'data/FRM-II',
        sample = 'Sample',
        propprefix = 'p',
        serviceexp = 'service',
        servicescript = '',
        templates = 'templates',
        sendmail = False,
    ),
    ANTARES = device('nicos.devices.instrument.Instrument',
        description = 'Antares Instrument',
        instrument = 'ANTARES',
        responsible = 'Michael Schulz <michael.schulz@frm2.tum.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-42',
        operators = [u'Technische Universität München (TUM)'],
        website = 'http://www.mlz-garching.de/antares',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
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
        lowlevel = True,
        warnlimits = (0.5, None),
    ),
)
