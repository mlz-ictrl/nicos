#  -*- coding: utf-8 -*-
description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'spodictrl.spodi.frm2',
    instrument = 'Spodi',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'spodilivesink',
        'spodisink',
    ],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Spodi = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'SPODI',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-24',
        responsible = 'Markus Hoelzel <markus.hoelzel@frm2.tum.de>',
        website = 'http://www.mlz-garching.de/spodi',
        operators = [
            u'Technische Universität München (TUM)',
            u'Karlsruher Institut für Technologie (KIT)',
        ],
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The current used sample',
    ),

    Exp = device('nicos_mlz.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/data',
        propdb = '/spodicontrol/propdb',
        sendmail = False,
        serviceexp = 'p0',
        sample = 'Sample',
        mailsender = 'spodi@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        elog = True,
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o644,
            disableDirMode = 0o550,
            disableFileMode = 0o440,
            owner = 'spodi',
            group = 'spodi'
        ),
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    spodilivesink = device('nicos_mlz.spodi.devices.datasinks.LiveViewSink',
        correctionfile='nicos_mlz/spodi/data/detcorrection.dat'
    ),
    spodisink = device('nicos_mlz.spodi.devices.datasinks.CaressHistogram',
        description = 'SPODI specific histogram file format',
        filenametemplate = ['run%(pointcounter)06d.ctxt'],
        detectors = ['adet'],
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = '/data',
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = '/spodicontrol/log',
        minfree = 0.5,
        lowlevel = True,
    ),
)

display_order = 70
