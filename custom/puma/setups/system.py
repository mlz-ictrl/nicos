#  -*- coding: utf-8 -*-

description = 'system setup for PUMA'

includes = ['puma']

sysconfig = dict(
    cache = 'pumahw',
    instrument = 'puma',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

devices = dict(
    Exp      = device('nicos.experiment.Experiment',
                      sample = 'Sample',
                      dataroot = '/data',
                      propdb = 'useroffice@tacodb.taco.frm2:useroffice',
                      ),
    Sample   = device('nicos.tas.TASSample'),
    filesink = device('nicos.data.AsciiDatafileSink',
                      globalcounter = '/data/filecounter'),
    conssink = device('nicos.data.ConsoleSink'),
#    liveplot = device('nicos.data.GraceSink'),
    daemonsink = device('nicos.data.DaemonSink'),
)

startupcode = '''
'''
