# -*- coding: utf-8 -*-
# description: Description of the setup (detailed)
description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

includes = [
    'notifiers',
    'coiltemp',
]

devices = dict(
    NSE = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'J-NSE',
        responsible = 'O. Holderer <o.holderer@fz-juelich.de>',
        operators = [u'Jülich Centre for Neutron Science (JCNS)'],
        website = 'http://www.mlz-garching.de/j-nse',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        # cannot use /data until main instrument control is switched to NICOS
        dataroot = '/home/jcns/nicos-data',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        lowlevel = True,
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        lowlevel = True,
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        lowlevel = True,
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
)
