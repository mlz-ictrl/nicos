description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument='YMIR',
    experiment='Exp',
    datasinks=['conssink', 'daemonsink', 'liveview', 'FileWriterControl'],
)

modules = [
    'nicos.commands.standard', 'nicos_ess.commands'
]

devices = dict(
    YMIR=device(
        'nicos.devices.instrument.Instrument',
        description='instrument object',
        instrument='YMIR',
        responsible='M. Clarke <matt.clarke@ess.eu>',
    ),
    Sample=device(
        'nicos_ess.devices.sample.EssSample',
        description='The currently used sample',
    ),
    Exp=device('nicos_ess.devices.experiment.EssExperiment',
                description='experiment object',
                dataroot='/opt/nicos-data',
                filewriter_root='/opt/nicos-data/ymir',
                sample='Sample',
                cache_filepath='/opt/nicos-data/ymir/cached_proposals.json'),
    conssink=device('nicos.devices.datasinks.ConsoleScanSink',),
    daemonsink=device('nicos.devices.datasinks.DaemonSink',),
    Space=device(
        'nicos.devices.generic.FreeSpace',
        description='The amount of free space for storing data',
        path=None,
        minfree=5,
    ),
    liveview=device('nicos.devices.datasinks.LiveViewSink', ),
    NexusStructure_Basic=device(
        'nicos_ess.devices.datasinks.nexus_structure.NexusStructureJsonFile',
        description='Provides the NeXus structure',
        nexus_config_path='nicos_ess/ymir/nexus/ymir_basic.json',
        visibility=(),
    ),
    NexusStructure_AreaDetector=device(
        'nicos_ess.devices.datasinks.nexus_structure.NexusStructureAreaDetector',
        description='Provides the NeXus structure',
        nexus_config_path='nicos_ess/ymir/nexus/ymir_ltomo.json',
        area_det_collector_device='area_detector_collector',
        visibility=(),
    ),
    NexusStructure=device(
        'nicos.devices.generic.DeviceAlias',
        alias='NexusStructure_AreaDetector',
        devclass=
        'nicos_ess.devices.datasinks.nexus_structure.NexusStructureJsonFile',
    ),
    FileWriterStatus=device(
        'nicos_ess.devices.datasinks.file_writer.FileWriterStatus',
        description='Status of the file-writer',
        brokers=['10.100.1.19:9092'],
        statustopic='ymir_filewriter',
        unit='',
    ),
    FileWriterControl=device(
        'nicos_ess.devices.datasinks.file_writer.FileWriterControlSink',
        description='Control for the file-writer',
        brokers=['10.100.1.19:9092'],
        pool_topic='ess_filewriter_pool',
        status='FileWriterStatus',
        nexus='NexusStructure',
        use_instrument_directory=True,
    ),
    SciChat=device(
        'nicos_ess.devices.scichat.ScichatBot',
        description='Connects to SciChat as a write-only client',
        url='https://server.scichat.esss.lu.se/_matrix/client/r0',
        room_id='!gaEXiGVYXizrNgFExx:ess',
    ),
)
