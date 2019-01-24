#  -*- coding: utf-8 -*-
description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'REFSANS',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'configsink'],
#   notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard', 'nicos_mlz.refsans.commands']

devices = dict(
    REFSANS = device('nicos.devices.instrument.Instrument',
        description = 'Container storing Instrument properties',
        instrument = 'REFSANS',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-31',
        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
        operators = ['NICOS developer team'],
        website = 'http://www.mlz-garching.de/refsans',
        facility = 'NICOS demo instruments',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'Container storing Sample properties',
    ),
    Exp = device('nicos_mlz.devices.experiment.Experiment',
        description = 'Container storing Experiment properties',
        propdb = 'propdb',
        dataroot = 'data',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        description = 'Device saving scanfiles',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        description = 'Device outputting logmessages to the console',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        description = 'The daemon Device, coordinating all the heavy lifting',
    ),
    configsink = device('nicos_mlz.refsans.devices.datasinks.ConfigObjDatafileSink',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free space on the log drive',
        path = 'log',
        lowlevel = True,
        warnlimits = (0.5, None),
    ),
)
