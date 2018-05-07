description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument=None,
    experiment='Exp',
    datasinks=['NexusDataSink'],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands.file_writing']

devices = dict(
    Sample=device('nicos.devices.sample.Sample',
        description='The current used sample',
        ),

    # Configure dataroot here (usually /data).
    Exp=device('nicos.devices.experiment.Experiment',
        description='experiment object',
        dataroot='/opt/nicos-data',
        sendmail=True,
        serviceexp='p0',
        sample='Sample',
        ),

    Space=device('nicos.devices.generic.FreeSpace',
        description='The amount of free space for storing data',
        path=None,
        minfree=5,
        ),

    NexusDataSink=device(
        'nicos_ess.devices.datasinks.nexussink.NexusFileWriterSink',
        description="Sink for NeXus file writer (kafka-to-nexus)",
        brokers=["192.168.12.109:9092"],
        cmdtopic="filewriter_cmds",
        status_provider='NexusFileWriter',
        templatesmodule='nicos_ess.integration.nexus.nexus_templates',
        templatename='integration_default',
    ),

    NexusFileWriter=device(
        'nicos_ess.devices.datasinks.nexussink.NexusFileWriterStatus',
        description="Status for nexus file writing",
        brokers=["192.168.12.109:9092"],
        statustopic="filewriter_status",
    )
)
