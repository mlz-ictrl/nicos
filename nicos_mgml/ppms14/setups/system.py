description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'ppms14',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    ppms14 = device('nicos.devices.instrument.Instrument',
        description = 'Experiment device for ppms14',
        instrument = 'PPMS14',
        responsible = 'Martin Žáček <zacekm@fzu.cz>',
        website = 'https://mgml.eu/laboratories/instruments/ppms14',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The current used sample',
    ),

    Cryostat = device('nicos.devices.generic.DeviceAlias'),

    Exp = device('nicos_mgml.devices.experiment.HeliumExperiment',
        description = 'experiment object',
        dataroot = '/data',
        sendmail = False,
        serviceexp = 'service',
        sample = 'Sample',
        cryostat = 'Cryostat'
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
)
