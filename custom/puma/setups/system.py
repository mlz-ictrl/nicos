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
    Exp      = device('devices.experiment.Experiment',
                      sample = 'Sample',
                      dataroot = '/data',
                      propdb = 'useroffice@tacodb.taco.frm2:useroffice',
                      ),
    Sample   = device('devices.tas.TASSample'),
    filesink = device('devices.datasinks.AsciiDatafileSink',
                      globalcounter = '/data/filecounter'),
    conssink = device('devices.datasinks.ConsoleSink'),
#    liveplot = device('devices.datasinks.GraceSink'),
    daemonsink = device('devices.datasinks.DaemonSink'),
)

startupcode = '''
'''
