#  -*- coding: utf-8 -*-
description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'stressictrl.stressi.frm2',
    instrument = 'Stressi',
    experiment = 'Exp',
    datasinks = [
        'conssink', 'daemonsink', 'livesink', 'LiveImgSink', 'LiveImgSinkLog'
    ],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Stressi = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'STRESS-SPEC',
        responsible = 'Dr. Michael Hofmann '
        '<michael.hofmann@frm2.tum.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-25',
        website = 'http://www.mlz-garching.de/stress-spec',
        operators = [
            u'Technische Universität München (TUM)',
            u'Technische Universität Clausthal',
            'German Engineering Materials Science Centre (GEMS)'
        ],
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The current used sample',
    ),

    Exp = device('nicos_mlz.devices.experiment.Experiment',
        description = 'The current running experiment',
        dataroot = '/data',
        sendmail = True,
        serviceexp = 'p0',
        sample = 'Sample',
        propdb = '/stressicontrol/propdb',
        propprefix = 'p',
        mailsender = 'stressi@frm2.tum.de',
        elog = True,
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o644,
            disableDirMode = 0o550,
            disableFileMode = 0o440,
            owner = 'stressi',
            group = 'stressi'
        ),
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = '/stressicontrol/log',
        minfree = 0.5,
        lowlevel = True,
    ),
    UBahn = device('nicos_mlz.devices.ubahn.UBahn',
        description = 'Next subway departures',
    ),
    caresssink = device('nicos_mlz.stressi.devices.datasinks.CaressScanfileSink',
        filenametemplate = ['m2%(scancounter)08d.dat'],
    ),
    yamlsink = device('nicos_mlz.stressi.devices.datasinks.YamlDatafileSink',
        filenametemplate = ['m2%(scancounter)08d.yaml'],
    ),
    LiveImgSinkLog = device('nicos.devices.datasinks.PNGLiveFileSink',
        description = 'Saves live image as .png every now and then',
        filename = '/stressicontrol/webroot/live_log.png',
        log10 = True,
        interval = 1,
    ),
    LiveImgSink = device('nicos.devices.datasinks.PNGLiveFileSink',
        description = 'Saves live image as .png every now and then',
        filename = '/stressicontrol/webroot/live_lin.png',
        interval = 1,
    ),
)
