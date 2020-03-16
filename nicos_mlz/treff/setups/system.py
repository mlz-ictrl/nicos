#  -*- coding: utf-8 -*-
description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'Treff',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard', 'nicos_mlz.maria.scan']

includes = ['notifiers']

devices = dict(
    Treff = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'TREFF',
        responsible = 'Egor Vehzlev <e.vehzlev@fz-juelich.de>',
        website = 'http://www.mlz-garching.de',
        operators = [
            u'Jülich Centre for Neutron Science (JCNS)',
            u'Technische Universität München (TUM)',
        ],
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),

    # Configure dataroot here (usually /data).
    Exp = device('nicos_mlz.devices.experiment.Experiment',
        description = 'Experiment object',
        dataroot = '/data',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o644,
            disableDirMode = 0o750,
            disableFileMode = 0o440,
            enableOwner = 'jcns',
            enableGroup = 'games',
            disableOwner = 'jcns',
            disableGroup = 'treff',
        ),
        propdb = '/home/jcns/.propdb',
        mailsender = 'treff@frm2.tum.de',
        sendmail = True,
        zipdata = True,
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
