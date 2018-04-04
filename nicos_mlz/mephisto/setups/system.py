# -*- coding: utf-8 -*-
description = 'system setup'

sysconfig = dict(
    cache = None, # 'sans1ctrl.sans1.frm2',
    instrument = 'MEPHISTO',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Sample = device('nicos.devices.sample.Sample',
        description = 'Container storing Sample properties',
    ),
    MEPHISTO = device('nicos.devices.instrument.Instrument',
        description = 'Facility for particle physics with cold '
        'neutrons',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-48',
        responsible = 'Dr. Jens Klenke <jens.klenke@frm2.tum.de>',
        operators = [u'Technische Universität München (TUM)'],
        website = 'http://www.mlz-garching.de/mephisto',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'MEPHISTO Experiment ',
        dataroot = '/localhome/data',
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
        minfree = 0.5,
    ),
)
