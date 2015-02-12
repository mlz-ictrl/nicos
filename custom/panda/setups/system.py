#  -*- coding: utf-8 -*-

description = 'system setup for PANDA'

group = 'lowlevel'

sysconfig = dict(
    cache = 'pandasrv',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
    instrument = 'panda',
    experiment = 'Exp',
)

modules = ['nicos.commands.standard']

devices = dict(
    Exp      = device('panda.experiment.PandaExperiment',
                      description = 'Experiment device for Panda',
                      localcontact = 'Astrid.Schneidewind@frm2.tum.de',
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
                      mailserver = 'smtp.frm2.tum.de',
                      mailsender = 'panda@frm2.tum.de',
                      serviceexp = 'service',
                      editor = '', #dont want editor anymore
                      scancounter = 'filecounter', #backwards compatibility
                      ),

    panda = device('devices.instrument.Instrument',
                    description = 'the spectrometer panda',
                    instrument = 'PANDA',
                    responsible = 'Astrid Schneidewind ' +
                                  '<astrid.schneidewind@frm2.tum.de>',
                  ),
    Sample   = device('devices.tas.TASSample',
                       description = 'Sample under investigation',
                     ),

    filesink = device('devices.datasinks.AsciiDatafileSink',
                       description = 'metadevice storing the scanfiles',
                       filenametemplate = ['%(proposal)s_%(counter)08d.dat',
                                           '/%(year)d/links/'
                                           '%(proposal)s_%(counter)08d.dat'],
                     ),
    conssink = device('devices.datasinks.ConsoleSink',
                       description = 'device used for console-output',
                     ),
    daemonsink  = device('devices.datasinks.DaemonSink',
                          description = 'device used for output from the daemon',
                        ),
)
