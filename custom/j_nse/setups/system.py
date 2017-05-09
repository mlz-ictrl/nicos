# description: Description of the setup (detailed)
description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['commands.standard']

includes = [
    'notifiers',
]

devices = dict(
    NSE = device('devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'J-NSE',
        responsible = 'O. Holderer <o.holderer@fz-juelich.de>',
    ),
    Sample = device('devices.sample.Sample',
        description = 'The currently used sample',
    ),

    Exp = device('devices.experiment.Experiment',
        description = 'experiment object',
        # cannot use /data until main instrument control is switched to NICOS
        dataroot = '/home/jcns/nicos-data',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
    ),
    filesink = device('devices.datasinks.AsciiScanfileSink',
        lowlevel = True,
    ),
    conssink = device('devices.datasinks.ConsoleScanSink',
        lowlevel = True,
    ),
    daemonsink = device('devices.datasinks.DaemonSink',
        lowlevel = True,
    ),
    Space = device('devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
)
