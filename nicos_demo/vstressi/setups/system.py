#  -*- coding: utf-8 -*-
description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'Stressi',
    experiment = 'Exp',
    datasinks = [
        'conssink', 'daemonsink', 'livesink', 'LiveImgSink', 'LiveImgSinkLog'
    ],
    # notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

# includes = ['notifiers']

devices = dict(
    Stressi = device('nicos.devices.instrument.Instrument',
        description = 'Virtual STRESSI instrument',
        instrument = 'V-Stress-Spec',
        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-25',
        website = 'http://www.mlz-garching.de/stress-spec',
        facility = 'NICOS demo instruments',
        operators = ['NICOS developer team'],
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The current used sample',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'The current running experiment',
        dataroot = 'data',
        sendmail = True,
        serviceexp = 'p0',
        sample = 'Sample',
        reporttemplate = '',
        elog = True,
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o644,
            disableDirMode = 0o550,
            disableFileMode = 0o440,
            # owner = 'stressi',
            # group = 'stressi'
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
        path = 'data',
        minfree = 5,
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
        filename = 'webroot/live_log.png',
        log10 = True,
        interval = 1,
    ),
    LiveImgSink = device('nicos.devices.datasinks.PNGLiveFileSink',
        description = 'Saves live image as .png every now and then',
        filename = 'webroot/live_lin.png',
        interval = 1,
    ),
)
