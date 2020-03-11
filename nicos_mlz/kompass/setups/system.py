#  -*- coding: utf-8 -*-
description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'kompassctrl',
    instrument = 'Kompass',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Kompass = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'KOMPASS',
        responsible = 'Dmitry Gorkov <dmitry.gorkov@frm2.tum.de>',
        # doi = 'http://dx.doi.org/10.17815/jlsrf-1-25',
        website = 'http://www.mlz-garching.de/kompass',
        operators = [
            'Technische Universität München (TUM)',
            'Universität zu Köln',
        ],
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
    Exp = device('nicos_mlz.devices.experiment.Experiment',
        description = 'The currently running experiment',
        dataroot = '/data',
        sample = 'Sample',
        serviceexp = 'service',
        sendmail = True,
        mailsender = 'kompass@frm2.tum.de',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o550,
            disableFileMode = 0o440,
            owner = 'kompassuser',
            group = 'kompass',
        ),
        elog = True,
        counterfile = 'counter',
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
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free space on the log drive',
        path = '/kompasscontrol/log',
        lowlevel = True,
        warnlimits = (0.5, None),
    ),
)
