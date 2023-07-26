description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument='DREAM',
    experiment='Exp',
    datasinks=['conssink', 'daemonsink', 'liveview', 'FileWriterControl'],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands']

devices = dict(
    DREAM=device(
        'nicos.devices.instrument.Instrument',
        description='instrument object',
        instrument='DREAM',
        responsible='Ebad Kamil <ebad.kamil@ess.eu>',
        website='https://europeanspallationsource.se/instruments/dream'),
    Sample=device(
        'nicos_ess.devices.sample.EssSample',
        description='The currently used sample',
    ),
    Exp=device('nicos_ess.devices.experiment.EssExperiment',
               description='experiment object',
               dataroot='/opt/nicos-data',
               sample='Sample',
               cache_filepath='/opt/nicos-data/dream/cached_proposals.json'),
    conssink=device(
        'nicos_ess.devices.datasinks.console_scan_sink.ConsoleScanSink'),
    daemonsink=device('nicos.devices.datasinks.DaemonSink', ),
    liveview=device('nicos.devices.datasinks.LiveViewSink', ),
    KafkaForwarderStatus=device(
        'nicos_ess.devices.forwarder.EpicsKafkaForwarder',
        description='Monitors the status of the Forwarder',
        statustopic="status_topic",
        brokers=["localhost"],
    ),
    NexusStructure=device(
        'nicos_ess.devices.datasinks.nexus_structure.NexusStructureJsonFile',
        description='Provides the NeXus structure',
        nexus_config_path="nicos_ess/dream/nexus/nexus_config.json",
        visibility=(),
    ),
    FileWriterStatus=device(
        'nicos_ess.devices.datasinks.file_writer.FileWriterStatus',
        description='Status of the file-writer',
        brokers=['localhost:9092'],
        statustopic='DREAM_controlTopic',
        unit='',
    ),
    FileWriterControl=device(
        'nicos_ess.devices.datasinks.file_writer.FileWriterControlSink',
        description='Control for the file-writer',
        brokers=['localhost:9092'],
        pool_topic='DREAM_jobPool',
        status='FileWriterStatus',
        nexus='NexusStructure',
    ),
)

startupcode = '''
'''
