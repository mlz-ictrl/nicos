# -*- coding: utf-8 -*-
description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'nectarhw.nectar.frm2',
    instrument = 'Instrument',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.basic', 'nicos.commands.standard',
           'nicos_mlz.antares.commands', 'nicos_mlz.nectar.commands']

includes = ['notifiers']

devices = dict(
    Sample = device('nicos.devices.sample.Sample',
        description = 'sample object',
    ),
    Exp = device('nicos_mlz.antares.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/data/FRM-II',
        propdb = '/etc/propdb',
        serviceexp = 'service',
        sample = 'Sample',
        mailsender = 'nectar@frm2.tum.de',
        sendmail = False,
        zipdata = False,
        managerights = {},
    ),
    Instrument = device('nicos.devices.instrument.Instrument',
        description = 'NECTAR instrument',
        instrument = 'NECTAR',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-45',
        responsible = 'Malgorzata Makowska <malgorzata.makowska@frm2.tum.de>',
        operators = [u'Technische Universität München (TUM)'],
        website = 'http://www.mlz-garching.de/nectar',
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
