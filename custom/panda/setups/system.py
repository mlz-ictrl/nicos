#  -*- coding: utf-8 -*-

name = 'system setup for PANDA'

sysconfig = dict(
    cache = 'pandasrv',
    instrument = 'panda',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink'],
    notifiers = [],
)

devices = dict(
    panda    = device('nicos.instrument.Instrument'),
    Exp      = device('nicos.panda.experiment.PandaExperiment',
                      sample = 'Sample',
                      datapath = ['/data']),
    Sample   = device('nicos.tas.TASSample'),
    filesink = device('nicos.data.AsciiDatafileSink',
                      globalcounter = '/data/filecounter'),
    conssink = device('nicos.data.ConsoleSink'),
)
