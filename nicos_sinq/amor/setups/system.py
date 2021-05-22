description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'Amor',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink', 'NexusDataSink'],
)

modules = [
    'nicos.commands.standard', 'nicos_ess.commands.file_writing',
    'nicos_sinq.amor.commands', 'nicos_sinq.commands.sics'
]

includes = ['sample', 'placeholders']

display_order = 30

devices = dict(
    Amor = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'SINQ AMOR',
        responsible = 'Jochen Stahn <jochen.stahn@psi.ch>',
        operators = ['Paul-Scherrer-Institut (PSI)'],
        facility = 'SINQ, PSI',
        website = 'https://www.psi.ch/sinq/amor/amor'
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
    Exp = device('nicos_sinq.amor.devices.experiment.AmorExperiment',
        description = 'experiment object',
        dataroot = '/home/amor/',
        sample = 'Sample'
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
        lowlevel = True,
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    KafkaForwarder = device('nicos_ess.devices.forwarder.EpicsKafkaForwarder',
        description = "Status of the epics-to-kafka forwarder",
        statustopic = configdata('config.FORWARDER_STATUS_TOPIC'),
        brokers = configdata('config.KAFKA_BROKERS'),
    ),
    NexusDataSink = device('nicos_sinq.devices.datasinks.SinqNexusFileSink',
        description = 'Sink for NeXus file writer (kafka-to-nexus)',
        brokers = configdata('config.KAFKA_BROKERS'),
        cmdtopic = configdata('config.FILEWRITER_COMMAND_TOPIC'),
        filenametemplate = ['amor%(year)sn%(pointcounter)06d.hdf'],
        status_provider = 'NexusFileWriter',
        templatesmodule = 'nicos_sinq.amor.nexus.nexus_templates',
        templatename = 'amor_commissioning'
    ),
    NexusFileWriter = device(
        'nicos_ess.devices.datasinks.nexussink.NexusFileWriterStatus',
        description = 'Status for nexus file writing',
        brokers = configdata('config.KAFKA_BROKERS'),
        statustopic = configdata('config.FILEWRITER_STATUS_TOPIC'),
    ),
    proton_current = device('nicos_sinq.devices.epics.proton_counter.SINQProtonCurrent',
        description = 'Proton current monitor',
        readpv = 'MHC6:IST:2',
        unit = 'uA',
        fmtstr = '%3.0f',
        pollinterval = 2,
    ),
)
