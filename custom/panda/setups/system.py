#  -*- coding: utf-8 -*-

name = 'system setup for PANDA'

includes=['detector']

sysconfig = dict(
    cache = 'pandasrv',
    instrument = 'panda',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink'],
    notifiers = [],
)

devices = dict(
    panda = device('nicos.instrument.Instrument',
                    instrument='Panda',
                    responsible='R.esponsible R@espons.ible',
                    ),
    Exp      = device('nicos.panda.experiment.PandaExperiment',
                      sample = 'Sample',
                      datapath = ['/data'],
                      ),
    Sample   = device('nicos.tas.TASSample'),
    filesink = device('nicos.data.AsciiDatafileSink',
                      globalcounter = '/data/filecounter'),
    conssink = device('nicos.data.ConsoleSink'),
)

startupcode='Exp.detectors.append(det)'
