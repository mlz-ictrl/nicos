# -*- coding: utf-8 -*-
description = 'system setup'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'PGAA_',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = ['nicos.commands.standard', 'nicos_mlz.pgaa.commands']

group = 'lowlevel'


devices = dict(
    Sample = device('nicos.devices.sample.Sample',
        description = 'The sample',
    ),
    PGAA_ = device('nicos.devices.instrument.Instrument',
        description = 'Prompt gamma and in-beam neutron activation analysis '
                      'facility',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-46',
        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
        operators = ['NICOS developer team'],
        website = 'http://www.mlz-garching.de/pgaa',
        facility = 'NICOS demo instruments',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'The currently running experiment',
        dataroot = 'data/',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing log files',
        warnlimits = (10, None),
        minfree = 5,
        path = 'log/',
        lowlevel = True,
    ),
)
