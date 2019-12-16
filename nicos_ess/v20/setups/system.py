description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'daemonsink', 'NexusDataSink'],
#    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands.file_writing',
           'nicos_ess.v20.commands.filewriter']

#includes = ['notifiers']

devices = dict(
    V20 = device('nicos.devices.instrument.Instrument',
                      description = 'instrument object',
                      instrument = 'V20',
                      responsible = 'Robin Woracek <robin.woracek@esss.se>',
                      facility='Helmholtz Zentrum Berlin',
                      website='https://www.helmholtz-berlin.de/pubbin/igama_output?' \
                              'modus=einzel&sprache=de&gid=1845&typoid=50726'
                     ),

    Sample   = device('nicos.devices.sample.Sample',
                      description = 'The currently used sample',
                     ),

    Exp      = device('nicos.devices.experiment.Experiment',
                      description = 'experiment object',
                      dataroot = '/opt/nicos-data/data',
                      sendmail = True,
                      serviceexp = 'p0',
                      sample = 'Sample',
                     ),

    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
                     ),

    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
                     ),

    daemonsink = device('nicos.devices.datasinks.DaemonSink',
                       ),

    Space    = device('nicos.devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      path = '/opt/nicos-data/data',
                      minfree = 5,
                     ),

    NexusDataSink=device(
        'nicos_ess.devices.datasinks.nexussink.NexusFileWriterSink',
        description="Sink for NeXus file writer (kafka-to-nexus)",
        brokers=["192.168.1.80:9092"],
        cmdtopic="V20_writerCommand",
        status_provider='NexusFileWriter',
        templatesmodule='nicos_ess.v20.nexus.nexus_templates',
        templatename='essiip_default',
        start_fw_file='/opt/nicos-core/nicos_ess/v20/V20_file_write_start.json',
    ),

    NexusFileWriter=device(
        'nicos_ess.devices.datasinks.nexussink.NexusFileWriterStatus',
        description="Status for nexus file writing",
        brokers=["192.168.1.80:9092"],
        statustopic="V20_writerStatus",
    ),
)

