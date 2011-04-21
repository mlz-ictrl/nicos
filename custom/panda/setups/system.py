#  -*- coding: utf-8 -*-

name = 'system setup for PANDA'

#includes = []

devices = dict(

    # -- System devices -------------------------------------------------------

    System   = device('nicos.system.System',
                      datapath = '/data',
                      cache = 'Cache',
                      datasinks = ['conssink', 'filesink'],
                      instrument = 'panda',
                      experiment = 'Exp',
                      notifiers = []),

    Exp      = device('nicos.panda.experiment.PandaExperiment',
                      sample = 'Sample'),
    
    Sample = device('nicos.tas.TASSample'),
    
    panda = device('nicos.instrument.Instrument'),

    filesink = device('nicos.data.AsciiDatafileSink',
                      globalcounter = '/data/filecounter'),

    conssink = device('nicos.data.ConsoleSink'),

    Cache    = device('nicos.cache.client.CacheClient',
                      lowlevel = True,
                      server = 'pandasrv',
                      prefix = 'nicos/',
                      loglevel = 'info'),

)
