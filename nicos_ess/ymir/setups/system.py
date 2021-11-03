description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument='YMIR',
    experiment='Exp',
    datasinks=['conssink', 'filesink', 'daemonsink', 'liveview',
               'FileWriterControl'],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands.epics']

devices = dict(
    YMIR=device('nicos.devices.instrument.Instrument',
                description='instrument object',
                instrument='YMIR',
                responsible='M. Clarke <matt.clarke@ess.eu>',
                ),

    Sample=device('nicos.devices.sample.Sample',
                  description='The currently used sample',
                  ),

    Exp=device('nicos_ess.devices.experiment.EssExperiment',
               description="The current experiment",
               dataroot='/opt/nicos-data/ymir',
               sample='Sample',
               server_url='https://useroffice-test.esss.lu.se/graphql',
               instrument='YMIR',
               cache_filepath='/opt/nicos-data/ymir/cached_proposals.json'
               ),

    filesink=device('nicos.devices.datasinks.AsciiScanfileSink',
                    ),

    conssink=device('nicos.devices.datasinks.ConsoleScanSink',
                    ),

    daemonsink=device('nicos.devices.datasinks.DaemonSink',
                      ),

    Space=device('nicos.devices.generic.FreeSpace',
                 description='The amount of free space for storing data',
                 path=None,
                 minfree=5,
                 ),

    liveview=device('nicos.devices.datasinks.LiveViewSink', ),

    NexusStructure=device(
        'nicos_ess.devices.datasinks.nexus_structure.NexusStructureJsonFile',
        description='Provides the NeXus structure',
        nexus_config_path='nicos_ess/ymir/nexus/ymir_basic.json',
        lowlevel=True,
    ),
    FileWriterStatus=device(
        'nicos_ess.devices.datasinks.file_writer.FileWriterStatus',
        description='Status of the file-writer',
        brokers=['172.30.242.20:9092'],
        statustopic='UTGARD_controlTopic',
        unit='',
    ),
    FileWriterControl=device(
        'nicos_ess.devices.datasinks.file_writer.FileWriterControlSink',
        description='Control for the file-writer',
        brokers=['172.30.242.20:9092'],
        pool_topic='UTGARD_writerJobPool',
        status='FileWriterStatus',
        nexus='NexusStructure',
    ),

)
