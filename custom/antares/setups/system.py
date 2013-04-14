#  -*- coding: utf-8 -*-

description = 'system setup'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'ANTARES',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = ['nicos.commands.standard']

devices = dict(
    Sample   = device('devices.tas.TASSample'),

    Exp      = device('devices.experiment.Experiment',
                      dataroot = '/home/antares/nicos-core/data',
                      sample = 'Sample'),

    ANTARES  = device('devices.instrument.Instrument',
                      instrument='ANTARES'),

    filesink = device('devices.datasinks.AsciiDatafileSink'),

    conssink = device('devices.datasinks.ConsoleSink'),
    daemonsink = device('devices.datasinks.DaemonSink'),

    Space    = device('devices.generic.FreeSpace',
                      path = '/',
                      minfree = 5),
)
