description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument='ESTIA',
    experiment='Exp',
    datasinks=['conssink', 'daemonsink'],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands']

includes = ['temp']

devices = dict(
    ESTIA=device(
        'nicos.devices.instrument.Instrument',
        description='instrument object',
        instrument='estia',
        responsible='Artur Glavic <artur.glavic@psi.ch>',
        website='https://confluence.esss.lu.se/display/ESTIA',
    ),
    Sample=device(
        'nicos.devices.sample.Sample',
        description='The currently used sample',
    ),
    Exp=device('nicos_ess.devices.experiment.EssExperiment',
               description='experiment object',
               dataroot=configdata('config.ESTIA_DATA_ROOT'),
               filewriter_root=configdata('config.ESTIA_FILEWRITER_ROOT'),
               sample='Sample',
               cache_filepath=f'{configdata("config.ESTIA_DATA_ROOT")}'
               f'/estia/cached_proposals.json'),
    conssink=device('nicos.devices.datasinks.ConsoleScanSink', ),
    daemonsink=device('nicos.devices.datasinks.DaemonSink', ),
    Space=device(
        'nicos.devices.generic.FreeSpace',
        description='The amount of free space for storing data',
        path=None,
        minfree=5,
    ),
    KafkaForwarderStatus=device(
        'nicos_ess.devices.forwarder.EpicsKafkaForwarder',
        description='Monitors the status of the Forwarder',
        statustopic="ESTIA_forwarderStatus",
        brokers=configdata('config.KAFKA_BROKERS'),
    ),
    NexusStructure=device(
        'nicos_ess.devices.datasinks.nexus_structure.NexusStructureJsonFile',
        description='Provides the NeXus structure',
        nexus_config_path="nicos_ess/estia/nexus/nexus_config.json",
        visibility=(),
    ),
    FileWriterStatus=device(
        'nicos_ess.devices.datasinks.file_writer.FileWriterStatus',
        description='Status of the file-writer',
        brokers=configdata('config.KAFKA_BROKERS'),
        statustopic='ESTIA_controlTopic',
        unit='',
    ),
    FileWriterControl=device(
        'nicos_ess.devices.datasinks.file_writer.FileWriterControlSink',
        description='Control for the file-writer',
        brokers=configdata('config.KAFKA_BROKERS'),
        pool_topic='ESTIA_jobPool',
        status='FileWriterStatus',
        nexus='NexusStructure',
    ),
)
