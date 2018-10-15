# -*- coding: utf-8 -*-
description = 'system setup for POWTEX'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'POWTEX',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Sample = device('nicos.devices.sample.Sample',
        description = 'Default Sample',
    ),

    Exp = device('nicos.devices.experiment.Experiment',
        description = 'POWTEX Experiment ',
        dataroot = '/home/crandau/data',
        sample = 'Sample',
        localcontact = 'andreas.houben@ac.rwth-aachen.de',
        propprefix = 'p',
        serviceexp = 'service',
        servicescript = '',
        templates = 'templates',
        sendmail = False,
        zipdata = False,
    ),
    POWTEX = device('nicos.devices.instrument.Instrument',
        description = 'POWTEX Instrument test',
        instrument = 'POWTEX',
        responsible = 'Andreas Houben <andreas.houben@ac.rwth-aachen.de>',
        operators = ['RWTH Aachen University',
                     u'Georg-August-Universität Göttingen',
                     u'Jülich Centre for Neutron Science (JCNS)'],
        website = 'http://www.mlz-garching.de/powtex',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        description = 'Device storing scanfiles in Ascii output format.',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        description = 'Device storing console output.',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        description = 'Device storing deamon output.',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
)
