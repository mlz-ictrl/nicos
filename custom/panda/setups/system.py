#  -*- coding: utf-8 -*-

description = 'system setup for PANDA'

group = 'lowlevel'

sysconfig = dict(
    cache = 'pandasrv',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'liveplot'],
    notifiers = [],
    instrument = 'panda',
    experiment = 'Exp',
)

modules = ['nicos.commands.standard']

devices = dict(
    Exp      = device('panda.experiment.PandaExperiment',
                      localcontact = 'Astrid.Schneidewind@frm2.tum.de',
                      sample = 'Sample',
                      dataroot = '/data',
                      propdb = 'useroffice@tacodb.taco.frm2:useroffice',
                      managerights = True,
                      sendmail = True,
                      zipdata = True,
                      mailserver = 'smtp.frm2.tum.de',
                      mailsender = 'panda@frm2.tum.de',
                      serviceexp = 'service',
                      editor = 'scite',
                      ),

    panda = device('devices.instrument.Instrument',
                    instrument = 'PANDA',
                    responsible = 'Astrid Schneidewind <astrid.schneidewind@frm2.tum.de>'),
    Sample   = device('devices.tas.TASSample'),

    filesink = device('devices.datasinks.AsciiDatafileSink',
                      globalcounter = '/data/filecounter'),

    conssink = device('devices.datasinks.ConsoleSink'),

    daemonsink  = device('devices.datasinks.DaemonSink'),

    liveplot = device('devices.datasinks.GraceSink'),
)
