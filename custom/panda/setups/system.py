#  -*- coding: utf-8 -*-

description = 'system setup for PANDA'

includes=['detector']

sysconfig = dict(
    cache = 'pandasrv',
    instrument = 'panda',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'liveplot'],
    notifiers = [],
)

devices = dict(
    panda = device('nicos.instrument.Instrument',
                    instrument='Panda',
                    responsible='R.esponsible R@espons.ible',
                    ),
    Exp      = device('nicos.panda.experiment.PandaExperiment',
                      sample = 'Sample',
                      dataroot = '/data',
                      propdb = 'useroffice@tacodb.taco.frm2:useroffice',
                      ),
    Sample   = device('nicos.tas.TASSample'),
    filesink = device('nicos.data.AsciiDatafileSink',
                      globalcounter = '/data/filecounter'),
    conssink = device('nicos.data.ConsoleSink'),
    liveplot = device('nicos.data.GraceSink',
                     activecounter='det2'),
)

startupcode='Exp.detectors.append(det)'
