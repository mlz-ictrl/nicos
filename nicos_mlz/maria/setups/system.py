# -*- coding: utf-8 -*-
description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'maria',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['mailer', 'smser'],
)

modules = ['nicos.commands.standard', 'nicos_mlz.maria.scan']

includes = ['notifiers']

devices = dict(
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),

    Exp = device('nicos_mlz.maria.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/data',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o644,
            disableDirMode = 0o750,
            disableFileMode = 0o440,
            enableOwner = 'jcns',
            enableGroup = 'games',
            disableOwner = 'jcns',
            disableGroup = 'maria',
        ),
        mailserver = 'mailhost.frm2.tum.de',
        mailsender = 'maria@frm2.tum.de',
        sendmail = True,
        zipdata = True,
        serviceexp = 'service',
        sample = 'Sample',
    ),
    maria = device('nicos.devices.instrument.Instrument',
        description = 'MAgnetic Reflectometer with Incident Angle',
        instrument = 'MARIA',
        responsible = 'Alexandros Koutsioumpas <a.koutsioumpas@fz-juelich.de>',
        operators = ['Jülich Centre for Neutron Science (JCNS)'],
        website = 'http://www.mlz-garching.de/maria',
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
