#  -*- coding: utf-8 -*-

name = 'system setup for PANDA'

#includes = []

sysconfig = dict(
    cache = 'pandasrv',
    instrument = 'panda',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink'],
    notifiers = [],
)

devices = dict(

    Exp      = device('nicos.panda.experiment.PandaExperiment',
                      sample = 'Sample'),
    
    Sample = device('nicos.tas.TASSample'),
    
    panda = device('nicos.instrument.Instrument'),

    filesink = device('nicos.data.AsciiDatafileSink',
                      globalcounter = '/data/filecounter'),

    conssink = device('nicos.data.ConsoleSink'),
)
