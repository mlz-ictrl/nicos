#  -*- coding: utf-8 -*-
description = 'NICOS system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'tofhw.toftof.frm2',
    instrument = 'TOFTOF',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'dmnsink', 'serialsink', 'livesink',
                 'tofsink'],
    notifiers = ['emailer', 'smser'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    TOFTOF = device('nicos.devices.instrument.Instrument',
                    description = 'The famous TOFTOF instrument',
                    responsible = 'W. Lohstroh <wiebke.lohstroh@frm2.tum.de>',
                    instrument = 'TOFTOF',
                    doi = 'http://dx.doi.org/10.17815/jlsrf-1-40',
                    website = 'http://www.mlz-garching.de/toftof',
                    operators = [u'Technische Universität München (TUM)'],
                   ),

    Sample = device('nicos.devices.sample.Sample',
                    description = 'The current used sample',
                   ),

    Exp = device('nicos_mlz.frm2.devices.experiment.Experiment',
                 description = 'The current running experiment',
                 dataroot = '/data',
                 sample = 'Sample',
                 serviceexp = '0',
                 propprefix = '',
                 sendmail = True,
                 mailsender = 'toftof@frm2.tum.de',
                 propdb = '/toftofcontrol/propdb',
                 managerights = dict(enableDirMode=0o775,
                                     enableFileMode=0o664,
                                     disableDirMode=0o550,
                                     disableFileMode=0o440,
                                     owner='toftof', group='toftof',
                                    ),
                 elog = True,
                 counterfile = 'counter',
                ),

    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
                      lowlevel = True,
                     ),

    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
                      lowlevel = True,
                     ),

    dmnsink = device('nicos.devices.datasinks.DaemonSink',
                     lowlevel = True,
                    ),

    serialsink = device('nicos.devices.datasinks.SerializedSink',
                        lowlevel = True,
                       ),

    livesink   = device('nicos_mlz.toftof.devices.datasinks.ToftofLiveViewSink',
                        lowlevel = True,
                       ),
    tofsink = device('nicos_mlz.toftof.devices.datasinks.TofImageSink',
                     filenametemplate = ['%(pointcounter)08d_0000.raw'],
                     lowlevel = True,
                    ),
    Space = device('nicos.devices.generic.FreeSpace',
                   description = 'The amount of free space for storing data',
                   path = '/data',
                   minfree = 5,
                  ),
)
