# -*- coding: utf-8 -*-
description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'ictrlfs.ictrl.frm2',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Instrument = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'ictrl',
        responsible = u'Jens Krüger <jens.krueger@frm2.tum.de>',
        operators = [u'Technische Universität München (TUM)'],
        website = 'http://www.mlz-garching.de/',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The current used sample',
    ),

    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = 'data',
        sendmail = False,
        serviceexp = 'p0',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
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
