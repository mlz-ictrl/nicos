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
    Sample   = device('devices.tas.TASSample'),

    Exp      = device('devices.experiment.Experiment',
                      dataroot = '/home/antares/nicos-core/data',
                      sample = 'Sample', _propdb='useroffice@tacodb.taco.frm2:useroffice'),

    ANTARES  = device('devices.instrument.Instrument', instrument='ANTARES'),

    filesink = device('devices.datasinks.AsciiDatafileSink',
                      prefix = 'data'),

    conssink = device('devices.datasinks.ConsoleSink'),
    daemonsink = device('devices.datasinks.DaemonSink'),

    Space    = device('devices.datasinks.FreeSpace',
                      path = '/',
                      minfree = 5),
)
