description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'SANS',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink', 'livesink'],
)

modules = [
    'nicos.commands.standard',
    'nicos_sinq.commands.sics',
    'nicos_sinq.commands.hmcommands',
    'nicos_sinq.commands.epicscommands',
]

devices = dict(
    SANS = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'SINQ SANS',
        responsible = 'Joachim Kohlbrecher <joachim.kohlbrecher@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/sans/',
    ),
    Sample = device('nicos.devices.experiment.Sample',
        description = 'The currently used sample',
    ),
    Exp = device('nicos_sinq.devices.experiment.SinqExperiment',
        description = 'experiment object',
        dataroot = configdata('config.DATA_PATH'),
        sendmail = False,
        serviceexp = 'Service',
        sample = 'Sample',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
        description = "Sink for forwarding live data to the GUI",
    ),
)
"""
    nxsink=device('nicos_sinq.nexus.nexussink.NexusSink',
           description="Sink for NeXus file writer",
           filenametemplate=['sans%(year)sn%(scancounter)06d.hdf'],
           templatesmodule='nicos_sinq.sans.nexus.nexus_templates',
           templateclass='SANSTemplateProvider',
           ),
    nxsink=device('nicos_sinq.sans.devices.sansnexussink.SANSNexusSink',
           description="Sink for NeXus file writer",
           filenametemplate=['sans%(year)sn%(scancounter)06d.hdf'],
           templatesmodule='nicos_sinq.sans.nexus.nexus_templates',
           templateclass='SANSTemplateProvider',
           ),

"""
