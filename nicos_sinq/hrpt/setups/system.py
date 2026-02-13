description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'HRPT',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink', 'nxsink', 'livesink'],
)

modules = [
    'nicos.commands.standard', 'nicos_sinq.commands.sics',
    'nicos_sinq.commands.hmcommands', 'nicos_sinq.commands.epicscommands'
]

devices = dict(
    HRPT = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'SINQ HRPT',
        responsible = 'Vladimir Pomjakushin <vladimir.pomjakushin@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/hrpt/',
    ),
    Sample = device('nicos_sinq.devices.sample.PowderSample',
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
    nxsink = device('nicos.nexus.NexusSink',
        description = "Sink for NeXus file writer",
        filenametemplate = ['hrpt%(year)sn%(scancounter)06d.hdf'],
        templateclass =
        'nicos_sinq.hrpt.nexus.nexus_templates.HRPTTemplateProvider',
    ),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
        description = "Sink for forwarding live data to the GUI",
    ),
)
