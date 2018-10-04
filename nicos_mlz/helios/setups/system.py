# -*- coding: utf-8 -*-
description = 'system setup only'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'helios',
    experiment = 'Exp',
    notifiers = ['email'],
    datasinks = ['conssink', 'dmnsink'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        sample = 'Sample',
        dataroot = 'data',
        serviceexp = 'p0',
        sendmail = False,
        mailsender = 'peter.stein@frm2.tum.de',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'currently used sample',
    ),
    helios = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'helios',
        responsible = 'Peter Stein <peter.stein@frm2.tum.de>',
        operators = [u'Technische Universität München (TUM)'],
    ),
    # filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    #     semicolon = False,
    # ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    dmnsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'free space for data files',
        path = 'data',
        minfree = 10,
    ),
)
