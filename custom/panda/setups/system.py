#  -*- coding: utf-8 -*-

description = 'system setup for PANDA'

includes = ['detector']

sysconfig = dict(
    cache = 'pandasrv',
    instrument = 'panda',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'liveplot'],
    notifiers = [],
)

devices = dict(
    panda = device('devices.instrument.Instrument',
                    instrument='Panda',
                    responsible='R.esponsible R@espons.ible',
                    ),
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
                      ),
    Sample   = device('devices.tas.TASSample'),
    filesink = device('devices.datasinks.AsciiDatafileSink',
                      globalcounter = '/data/filecounter'),
    conssink = device('devices.datasinks.ConsoleSink'),
    liveplot = device('devices.datasinks.GraceSink'),
)

startupcode = 'Exp.detectors.append(det)'
