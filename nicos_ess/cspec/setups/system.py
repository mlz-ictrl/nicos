#  -*- coding: utf-8 -*-

description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'liveview'],
    notifiers = ['email'],
)

modules = ['nicos.commands.standard']

includes = [
    'notifiers',
]

devices = dict(
    cspec = device('nicos.devices.instrument.Instrument',
        description = 'CSPEC instrument',
        facility = 'European Spallation Source (ESS)',
        instrument = 'CSPEC',
        responsible = 'P.P. Deen <pascale.deen@esss.se>',
        website = 'https://europeanspallationsource.se/instruments/cspec',
        operators = ['European Spallation Source (ESS)',
                     'Technische Universität München (TUM)',
        ]
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = 'data',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        visibility = (),
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        visibility = (),
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        visibility = (),
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
    liveview=device('nicos.devices.datasinks.LiveViewSink', ),
)
