#  -*- coding: utf-8 -*-
description = 'NICOS system setup'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'SE',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'dmnsink'],
    notifiers = ['emailer', 'smser'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    SE = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        responsible = 'Alexander Weber <al.weber@fz-juelich.de>',
        instrument = 'SE',
        operators = ['Forschungszentrum Jülich, JCNS'],
        website = 'http://www.mlz-garching.de/se',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'sample object',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/data',
        sample = 'Sample',
        elog = False,
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    dmnsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The free space on the data storage',
        path = '/data',
        minfree = 5,
    ),
)
