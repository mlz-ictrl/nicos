# -*- coding: utf-8 -*-
description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'lauectrl.laue.frm2',
    instrument = 'Laue',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'dmnsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard',]

devices = dict(
    Laue = device('nicos.devices.instrument.Instrument',
        description = 'Laue camera',
        instrument = 'Laue',
        responsible = 'Dr. B. Pedersen <bjoern.pedersen@frm2.tum.de>',
        #  we do not have a dedicated responsible
        operators = [u'Technische Universität München (TUM)'],
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),

    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/data',
        sendmail = False,
        zipdata = False,
        serviceexp = 'service',
        strictservice = True,
        # We do not have a dedicated responsible
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    dmnsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
)

includes = ['notifiers',]
