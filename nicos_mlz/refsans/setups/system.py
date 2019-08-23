#  -*- coding: utf-8 -*-
description = 'system setup'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

code_base = instrument_values['code_base']
pc_ctrl = instrument_values['pc_ctrl']

sysconfig = dict(
    cache = pc_ctrl,
    instrument = 'REFSANS',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'configsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard', 'nicos_mlz.refsans.commands']
includes = ['notifiers']

devices = dict(
    REFSANS = device('nicos.devices.instrument.Instrument',
        description = 'Container storing Instrument properties',
        instrument = 'REFSANS',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-31',
        responsible = 'Dr. Jean-Francois Moulin <jean-francois.moulin@hzg.de>',
        operators = ['German Engineering Materials Science Centre (GEMS)'],
        website = 'http://www.mlz-garching.de/refsans',
    ),
    Sample = device(code_base + 'sample.Sample',
        description = 'Container storing Sample properties',
    ),
    Exp = device('nicos_mlz.devices.experiment.Experiment',
        description = 'Container storing Experiment properties',
        propdb = '/refsanscontrol/propdb',
        dataroot = '/data',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        description = 'Device saving scanfiles',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        description = 'Device outputting logmessages to the console',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    configsink = device(code_base + 'datasinks.ConfigObjDatafileSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free space on the log drive',
        path = '/refsanscontrol/log',
        lowlevel = True,
        warnlimits = (0.5, None),
    ),
)
