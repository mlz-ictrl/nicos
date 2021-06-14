# -*- coding: utf-8 -*-
description = 'system setup only'

group = 'lowlevel'

sysconfig = dict(
    cache = 'miractrl.mira.frm2',
    instrument = 'mira',
    experiment = 'Exp',
    notifiers = ['email', 'smser'],
    datasinks = ['conssink', 'filesink', 'dmnsink'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Exp = device('nicos_mlz.mira.devices.experiment.MiraExperiment',
        description = 'experiment object',
        sample = 'Sample',
        dataroot = '/data',
        serviceexp = '0',
        sendmail = True,
        mailsender = 'rgeorgii@frm2.tum.de',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'sample object',
    ),
    mira = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'MIRA',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-21',
        responsible = 'Robert Georgii <robert.georgii@frm2.tum.de>',
        operators = ['Technische Universität München (TUM)'],
        website = 'http://www.mlz-garching.de/mira',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    dmnsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'free space on data share',
        path = '/data',
        minfree = 10,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free space on the log drive',
        path = '/miracontrol/log',
        lowlevel = True,
        warnlimits = (0.5, None),
    ),
)
