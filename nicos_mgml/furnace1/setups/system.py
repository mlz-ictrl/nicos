description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'Furnace1',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = ['nicos.commands.standard']

includes = [
    'notifiers',
]

devices = dict(
    Furnace1 = device('nicos.devices.instrument.Instrument',
        description = 'Furnace number 1',
        instrument = 'Furnace 1',
        responsible = 'Jiri Pospisil <jiri.pospisil@centrum.cz>',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The current used sample',
    ),

    # Configure dataroot here (usually /data).
    Exp = device('nicos_mgml.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/storage/data',
        sendmail = False,
        serviceexp = 'service',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
)
