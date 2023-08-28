description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument='ESTIA',
    experiment='Exp',
    datasinks=['conssink', 'daemonsink', 'liveview', 'FileWriterControl'],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands']

includes = ['temp']

devices = dict(
    ESTIA=device(
        'nicos.devices.instrument.Instrument',
        description='instrument object',
        instrument='ESTIA',
        responsible='Artur Glavic <artur.glavic@psi.ch>',
    ),
    Sample=device(
        'nicos_ess.devices.sample.EssSample',
        description='The currently used sample',
    ),
    Exp=device('nicos_ess.devices.experiment.EssExperiment',
               description='experiment object',
               dataroot='/opt/nicos-data',
               sample='Sample',
               cache_filepath='/opt/nicos-data/cached_proposals.json'),
    conssink=device(
        'nicos_ess.devices.datasinks.console_scan_sink.ConsoleScanSink'),
    liveview=device('nicos.devices.datasinks.LiveViewSink', ),
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
        statustopic='estia_forwarder_status',
        brokers=['10.100.1.19:8093'],
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
        brokers=['10.100.1.19:8093'],
        statustopic='estia_filewriter',
        unit='',
    ),
    FileWriterControl=device(
        'nicos_ess.devices.datasinks.file_writer.FileWriterControlSink',
        description='Control for the file-writer',
        brokers=['10.100.1.19:8093'],
        pool_topic='ess_filewriter_pool',
        status='FileWriterStatus',
        nexus='NexusStructure',
        use_instrument_directory=True,
    ),
    SciChat=device(
        'nicos_ess.devices.scichat.ScichatBot',
        description='Sends messages to SciChat',
        brokers=['10.100.1.19:8093'],
    ),
)
