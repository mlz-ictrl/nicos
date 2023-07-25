description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument='BIFROST',
    experiment='Exp',
    datasinks=['conssink', 'daemonsink', 'liveview', 'FileWriterControl'],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands']

KAFKA_BROKERS = ["10.100.1.19:8093"]

devices = dict(
    BIFROST=device(
        'nicos.devices.instrument.Instrument',
        description='instrument object',
        facility='European Spallation Source (ERIC)',
        instrument='BIFROST',
        responsible='Rasmus Toft-Petersen <rasmus.toft-petersen@ess.eu>',
        website='https://europeanspallationsource.se/instruments/bifrost'),
    Sample=device(
        'nicos_ess.devices.sample.EssSample',
        description='The currently used sample',
    ),
    Exp=device('nicos_ess.devices.experiment.EssExperiment',
               description='experiment object',
               dataroot='/opt/nicos-data',
               filewriter_base='bifrost',
               sample='Sample',
               cache_filepath='/opt/nicos-data/bifrost/cached_proposals.json'),
    conssink=device(
        'nicos_ess.devices.datasinks.console_scan_sink.ConsoleScanSink'),
    daemonsink=device('nicos.devices.datasinks.DaemonSink', ),
    liveview=device('nicos.devices.datasinks.LiveViewSink', ),
    KafkaForwarderStatus=device(
        'nicos_ess.devices.forwarder.EpicsKafkaForwarder',
        description='Monitors the status of the Forwarder',
        statustopic="bifrost_forwarder_status",
        brokers=KAFKA_BROKERS,
    ),
    NexusStructure_Basic=device(
        'nicos_ess.devices.datasinks.nexus_structure.NexusStructureJsonFile',
        description='Provides the NeXus structure',
        nexus_config_path='nicos_ess/bifrost/nexus/bifrost_basic.json',
        visibility=(),
    ),
    NexusStructure=device(
        'nicos.devices.generic.DeviceAlias',
        alias='NexusStructure_Basic',
        devclass=
        'nicos_ess.devices.datasinks.nexus_structure.NexusStructureJsonFile',
    ),
    FileWriterStatus=device(
        'nicos_ess.devices.datasinks.file_writer.FileWriterStatus',
        description='Status of the file-writer',
        brokers=KAFKA_BROKERS,
        statustopic='bifrost_filewriter',
        unit='',
    ),
    FileWriterControl=device(
        'nicos_ess.devices.datasinks.file_writer.FileWriterControlSink',
        description='Control for the file-writer',
        brokers=KAFKA_BROKERS,
        pool_topic='ess_filewriter_pool',
        status='FileWriterStatus',
        nexus='NexusStructure',
        use_instrument_directory=True,
    ),
    SciChat=device(
        'nicos_ess.devices.scichat.ScichatBot',
        description='Sends messages to SciChat',
        brokers=KAFKA_BROKERS,
    ),
)
