description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'DMC',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink', 'livesink', 'NexusDataSink',
                 'quiecksink'],
)

modules = [
    'nicos.commands.standard', 'nicos_sinq.commands.sics'
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
        description = 'Sink for forwarding live data to the GUI',
    ),
    KafkaForwarder = device('nicos_ess.devices.forwarder.EpicsKafkaForwarder',
        description = 'Monitors and controls forward-epics-to-kafka',
        statustopic = configdata('config.FORWARDER_STATUS_TOPIC'),
        brokers = configdata('config.KAFKA_BROKERS'),
    ),
    NexusDataSink = device('nicos_sinq.devices.datasinks.SinqNexusFileSink',
        description = 'Sink for NeXus file writer (kafka-to-nexus)',
        brokers = configdata('config.KAFKA_BROKERS'),
        filenametemplate = ['dmc%(year)sn%(pointcounter)06d.hdf'],
        cmdtopic = 'DMC_filewriterCommands',
        cachetopic = 'DMC_nicosCacheHistory',
        useswmr = False,
        status_provider = 'NexusFileWriter',
        templatesmodule = 'nicos_sinq.dmc.nexus.nexus_templates',
        templatename = 'dmc_default'
    ),
    NexusFileWriter = device('nicos_ess.devices.datasinks.nexussink.NexusFileWriterStatus',
        description = 'Status for nexus file writing',
        brokers = configdata('config.KAFKA_BROKERS'),
        statustopic=configdata('config.FILEWRITER_STATUS_TOPIC'),
    ),
    quiecksink = device('nicos_sinq.devices.datasinks.QuieckSink',
        description = 'Sink for sending UDP datafile '
        'notifications'
    ),
)
