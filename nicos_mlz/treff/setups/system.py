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
                   # doi = 'http://dx.doi.org/10.17815/jlsrf-1-31',
                   responsible = 'Andreas Ofner<andreas.ofnert@frm2.tum.de>',
                   website = 'http://www.mlz-garching.de',
                   operators = [u'Technische Universität München (TUM)',
                                u'Jülich Center for Neutron Science (JCNS)',
                                ],
                  ),

    Sample   = device('nicos.devices.sample.Sample',
                      description = 'The current used sample',
                     ),

    # Configure dataroot here (usually /data).
    Exp      = device('nicos.devices.experiment.Experiment',
                      description = 'experiment object',
                      dataroot = '/data',
                      managerights = dict(enableDirMode=0o775,
                                          enableFileMode=0o644,
                                          disableDirMode=0o750,
                                          disableFileMode=0o440,
                                          enableOwner='jcns',
                                          enableGroup='games',
                                          disableOwner='jcns',
                                          disableGroup='treff',
                                         ),
                      mailserver = 'mailhost.frm2.tum.de',
                      mailsender = 'treff@frm2.tum.de',
                      sendmail = True,
                      zipdata = True,
                      serviceexp = 'service',
                      sample = 'Sample',
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

    Space    = device('nicos.devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      path = None,
                      minfree = 5,
                     ),
)
