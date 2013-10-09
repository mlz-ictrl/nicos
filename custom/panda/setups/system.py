#  -*- coding: utf-8 -*-

description = 'system setup for PANDA'

group = 'lowlevel'

sysconfig = dict(
    cache = 'pandasrv',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'liveplot'],
    notifiers = [],
    instrument = 'panda_boot',
    experiment = 'Exp',
)

modules = ['nicos.commands.standard']

devices = dict(
    Exp      = device('panda.experiment.PandaExperiment',
                       description = 'Experiment device for Panda',
                       localcontact = 'Astrid.Schneidewind@frm2.tum.de',
                       sample = 'Sample',
                       dataroot = '/data',
                       #templatedir = '/data/exp/template',
                       templatedir = '/pandacontrol/template',
                       propdb = '/pandacontrol/setups/special/propdb',
                       managerights = True,
                       sendmail = True,
                       zipdata = True,
                       mailserver = 'smtp.frm2.tum.de',
                       mailsender = 'panda@frm2.tum.de',
                       serviceexp = 'service',
                       editor = 'scite',
                     ),
    panda_boot = device('devices.instrument.Instrument',
                    description = 'the spectrometer panda',
                    instrument = 'PANDA',
                    responsible = 'Astrid Schneidewind <astrid.schneidewind@frm2.tum.de>',
                    lowlevel = True,
                  ),
    Sample   = device('devices.tas.TASSample',
                       description = 'Sample davice storing metadata',
                     ),
    filesink = device('devices.datasinks.AsciiDatafileSink',
                       description = 'metadevice storing the scanfiles',
                       globalcounter = '/data/filecounter',
                     ),
    conssink = device('devices.datasinks.ConsoleSink',
                       description = 'device used for console-output',
                     ),
    daemonsink  = device('devices.datasinks.DaemonSink',
                          description = 'device used for output from the daemon',
                        ),
    liveplot = device('devices.datasinks.GraceSink',
                        description = 'device handling the live-plot',
                     ),
)
