description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument='DREAM',
    experiment='Exp',
    datasinks=['conssink', 'daemonsink', 'liveview'],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands.epics',
           'nicos_ess.commands.file_writing']

devices = dict(
    DREAM=device(
        'nicos.devices.instrument.Instrument',
        description='instrument object',
        instrument='DREAM',
        responsible='Ebad Kamil <ebad.kamil@ess.eu>',
        website='https://europeanspallationsource.se/instruments/dream'
    ),

    Sample=device(
        'nicos.devices.sample.Sample',
        description='The currently used sample',
    ),

    Exp=device(
        'nicos_ess.devices.experiment.EssExperiment',
        description='experiment object',
        dataroot='/opt/nicos-data/dream',
        sendmail=False,
        serviceexp='p0',
        sample='Sample',
        server_url='https://useroffice-test.esss.lu.se/graphql',
        instrument='DREAM',
        cache_filepath='/opt/nicos-data/dream/cached_proposals.json'
    ),

    filesink=device('nicos.devices.datasinks.AsciiScanfileSink',),

    conssink=device('nicos.devices.datasinks.ConsoleScanSink',),

    daemonsink=device('nicos.devices.datasinks.DaemonSink',),
    liveview=device('nicos.devices.datasinks.LiveViewSink', ),

    Space=device(
        'nicos.devices.generic.FreeSpace',
        description='The amount of free space for storing data',
        path=None,
        minfree=5,
    ),

    KafkaForwarderStatus=device(
        'nicos_ess.devices.forwarder.EpicsKafkaForwarder',
        description='Monitors the status of the Forwarder',
        statustopic="status_topic",
        forwarder_control="KafkaForwarderControl",
        brokers=["localhost"],
    ),

    KafkaForwarderControl=device(
        'nicos_ess.devices.forwarder.EpicsKafkaForwarderControl',
        description='Controls the Forwarder',
        cmdtopic="TEST_forwarderConfig",
        instpvtopic="pv_topic",
        brokers=["localhost"],
    ),

    NexusDataSink=device(
        'nicos_ess.devices.datasinks.nexussink.NexusFileWriterSink',
        description='Sink for NeXus file writer (kafka-to-nexus)',
        brokers=['localhost:9092'],
        cmdtopic='FileWriter_writerCommand',
        status_provider='NexusFileWriter',
        templatesmodule='nicos_ess.dream_demo.nexus.nexus_templates',
        templatename='dream_default',
    ),

    NexusFileWriter=device(
        'nicos_ess.devices.datasinks.nexussink.NexusFileWriterStatus',
        description='Status for nexus file writing',
        brokers=['localhost:9092'],
        statustopic='FileWriter_writerStatus',
    ),
)

startupcode = '''
'''
