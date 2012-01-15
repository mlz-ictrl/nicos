#  -*- coding: utf-8 -*-

name = 'system setup'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'ANTARES',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

devices = dict(
    Sample   = device('nicos.tas.TASSample'),

    Exp      = device('nicos.experiment.Experiment',
                      datapath = ['/home/antares/nicos-core/data'],
                      sample = 'Sample', _propdb='useroffice@tacodb.taco.frm2:useroffice'),

    ANTARES  = device('nicos.instrument.Instrument', instrument='ANTARES'),

    filesink = device('nicos.data.AsciiDatafileSink',
                      prefix = 'data'),

    conssink = device('nicos.data.ConsoleSink'),
    daemonsink = device('nicos.data.DaemonSink'),

    Space    = device('nicos.data.FreeSpace',
                      path = '/',
                      minfree = 5),
)
