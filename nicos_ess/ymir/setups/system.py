description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument=None,
    experiment='Exp',
    datasinks=['conssink', 'filesink', 'daemonsink', 'liveview', ],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands.epics']

devices = dict(
    Skeleton=device('nicos.devices.instrument.Instrument',
                    description='instrument object',
                    instrument='ymir',
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
               instrument='YMIR'
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

    NexusDataSink=device(
        'nicos_ess.devices.datasinks.nexussink.NexusFileWriterSink',
        description='Sink for NeXus file writer (kafka-to-nexus)',
        brokers=['172.30.242.20:9092'],
        cmdtopic='UTGARD_writerCommand',
        status_provider='NexusFileWriter',
        templatesmodule='nicos_ess.ymir.nexus.nexus_templates',
        templatename='ymir_default'
    ),

    NexusFileWriter=device(
        'nicos_ess.devices.datasinks.nexussink.NexusFileWriterStatus',
        description='Status for nexus file writing',
        brokers=['172.30.242.20:9092'],
        statustopic='UTGARD_writerStatus',
    ),

)
