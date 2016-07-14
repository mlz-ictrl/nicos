#  -*- coding: utf-8 -*-
description = 'NICOS system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'tofhw.toftof.frm2',
    instrument = 'TOFTOF',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'dmnsink', 'serialsink', 'livesink',
                 'tofsink', ],
    notifiers = ['emailer', 'smser'],
)

modules = ['commands.standard']

includes = ['notifiers', ]

devices = dict(
    TOFTOF = device('devices.instrument.Instrument',
                    description = 'The famous TOFTOF instrument',
                    responsible = 'W. Lohstroh <wiebke.lohstroh@frm2.tum.de>',
                    instrument = 'TOFTOF',
                    doi = 'http://dx.doi.org/10.17815/jlsrf-1-40',
                    website = 'http://www.mlz-garching.de/toftof',
                    operators = [u'Technische Universität München (TUM)', ],
                   ),

    Sample = device('devices.sample.Sample',
                    description = 'The current used sample',
                   ),

    Exp = device('frm2.experiment.Experiment',
                 description = 'The current running experiment',
                 dataroot = '/data',
                 sample = 'Sample',
                 serviceexp = '0',
                 propprefix = '',
                 sendmail = True,
                 mailsender = 'nicos.toftof@frm2.tum.de',
                 propdb = '/opt/nicos/propdb',
                 managerights = dict(enableDirMode=0o775,
                                     enableFileMode=0o664,
                                     disableDirMode=0o550,
                                     disableFileMode=0o440,
                                     owner='toftof', group='toftof',
                                    ),
                 elog = True,
                 counterfile = 'counter',
                ),

    filesink = device('devices.datasinks.AsciiScanfileSink',
                      lowlevel = True,
                     ),

    conssink = device('devices.datasinks.ConsoleScanSink',
                      lowlevel = True,
                     ),

    dmnsink = device('devices.datasinks.DaemonSink',
                     lowlevel = True,
                    ),

    serialsink = device('devices.datasinks.SerializedSink',
                        lowlevel = True,
                       ),

    livesink   = device('toftof.datasinks.ToftofLiveViewSink',
                        lowlevel = True,
                       ),
    tofsink = device('toftof.datasinks.TofImageSink',
                     filenametemplate = ['%(pointcounter)08d_0000.raw'],
                     lowlevel = True,
                    ),
    Space = device('devices.generic.FreeSpace',
                   description = 'The amount of free space for storing data',
                   path = '/data',
                   minfree = 5,
                  ),
)
