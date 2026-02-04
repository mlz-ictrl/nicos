description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'DMC',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink', 'livesink', 'nxsink'],
)

modules = [
    'nicos.commands.standard', 'nicos_sinq.commands.sics',
    'nicos_sinq.commands.epicscommands'
]

devices = dict(
    DMC = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'SINQ DMC',
        responsible = 'Lukas Keller <lukas.keller@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/dmc/',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
    Exp = device('nicos_sinq.devices.experiment.SinqExperiment',
        description = 'experiment object',
        dataroot = configdata('config.DATA_PATH'),
        serviceexp = 'Service',
        sample = 'Sample',
        forcescandata = True,
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
        description = 'Sink for forwarding live data to the GUI',
    ),
    nxsink = device('nicos.nexus.nexussink.NexusSink',
        description = "Sink for NeXus file writer",
        filenametemplate = ['dmc%(year)sn%(scancounter)06d.hdf'],
        templateclass =
        'nicos_sinq.dmc.nexus.nexus_templates.DMCTemplateProvider',
    ),
)
