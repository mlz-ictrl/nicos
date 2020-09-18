# -*- coding: utf-8 -*-
description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'emc',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    emc = device('nicos.devices.instrument.Instrument',
        description = 'ElectroMagnetic Compatibility',
        instrument = 'EMC',
        responsible = 'F. Beule <f.beule@fz-juelich.de>',
        operators = ['Jülich Centre for Neutron Science (JCNS)'],
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),

    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = 'data',
        sendmail = False,
        serviceexp = 'service',
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
