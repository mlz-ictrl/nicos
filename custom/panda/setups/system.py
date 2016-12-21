#  -*- coding: utf-8 -*-

description = 'system setup for PANDA'

group = 'lowlevel'

sysconfig = dict(
    cache = 'phys.panda.frm2',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email'],
    instrument = 'panda',
    experiment = 'Exp',
)

modules = ['commands.standard']

includes = ['notifiers', ]

devices = dict(
    Exp      = device('panda.experiment.PandaExperiment',
                      description = 'Experiment device for Panda',
                      sample = 'Sample',
                      dataroot = '/data',
                      templates = 'templates',
                      propdb = '/usr/local/nicos/custom/panda/setups/special/propdb',
                      managerights = dict(enableDirMode=0o775,
                                          enableFileMode=0o664,
                                          disableDirMode=0o700,
                                          disableFileMode=0o600,
                                          owner='jcns', group='panda'),
                      sendmail = True,
                      zipdata = True,
                      mailserver = 'mailhost.frm2.tum.de',
                      mailsender = 'panda@frm2.tum.de',
                      serviceexp = 'service',
                      ),

    panda = device('devices.instrument.Instrument',
                    description = 'the PANDA spectrometer',
                    instrument = 'PANDA',
                    responsible = 'Astrid Schneidewind ' +
                                  '<astrid.schneidewind@frm2.tum.de>',
                   doi = 'http://dx.doi.org/10.17815/jlsrf-1-35',
                  ),
    Sample   = device('devices.tas.TASSample',
                       description = 'Sample under investigation',
                     ),

    filesink = device('devices.datasinks.AsciiScanfileSink',
                       description = 'metadevice storing the scanfiles',
                       filenametemplate = ['%(proposal)s_%(scancounter)08d.dat',
                                           '/%(year)d/links/'
                                           '%(proposal)s_'
                                           '%(scancounter)08d.dat'],
                     ),
    conssink = device('devices.datasinks.ConsoleScanSink',
                       description = 'device used for console-output',
                     ),
    daemonsink  = device('devices.datasinks.DaemonSink',
                          description = 'device used for output from the daemon',
                        ),
)
