# description: Description of the setup (detailed)
description = 'system setup'

# group: Group of the setup. The following groups are recognized:
# - basic
#       Basic setup for the instrument, of which only one should be
#       loaded (e.g. "twoaxis" or "threeaxis"). These setups can be
#       presented to the user.
# - optional
#       Optional setup, of which as many as needed can be loaded.
#       These setups can be presented to the user for multiple
#       selection. This is the default.
# - lowlevel
#       Low-level setup, which will be included by others, but should
#       not be presented to users.
# - special
#       The setup is not a setup of instrument devices, but configures
#       e.g. a NICOS service. For each service, there is one special
#       setup (e.g. "cache", "poller", "daemon").
group = 'lowlevel'

# sysconfig: A dictionary with basic system configuration values.
# Possible values:
#   - cache
#       A string giving the hostname[:port] of the cache server,
#       the default port is 14869.
#       If this value is omitted, no caching will be available.
#   - instrument
#       The name of the instrument device, defined somewhere in a
#       devices dictionary. The class for this device must be
#       nicos.devices.instrument.Instrument or an instrument-specific
#       subclass.
#   - experiment
#       The name of the experiment "device", defined somewhere in a
#       devices dictionary. The class for this device must be
#       nicos.devices.experiment.Experiment or an instrument-specific
#       subclass.
#   - datasinks
#       A list of names of "data sinks", i.e. special devices that
#       process measured data. These devices must be defined somewhere
#       in a devices dictionary and be of class
#       nicos.devices.datasinks.DataSink or a subclass.
#   - notifiers
#       A list of names of "notifiers", i.e. special devices that can
#       notify the user or instrument responsibles via various channels
#       (e.g. email). These devices must be defined somewhere in a
#       devices dictionary and be of class
#       nicos.devices.notifiers.Notifier or a subclass.

sysconfig = dict(
    cache='localhost',
    instrument='Amor',
    experiment='Exp',
    datasinks=['NexusDataSink', 'HistogramDataSink'],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands.file_writing',
           'nicos_sinq.amor.commands']

# devices: Contains all device definitions.
# A device definition consists of a call like device(classname, parameters).
# The class name is fully qualified (i.e., includes the package/module name).
# The parameters are given as keyword arguments.
devices = dict(
    Amor=device('nicos.devices.instrument.Instrument',
                description='instrument object',
                instrument='SINQ AMOR',
                responsible='Nikhil Biyani <nikhil.biyani@psi.ch>',
                operators=['Paul-Scherrer-Institut (PSI)'],
                ),

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

    KafkaForwarder=device(
        'nicos_ess.devices.forwarder.EpicsKafkaForwarder',
        description="Configures commands to forward-epics-to-kafka",
        cmdtopic="forward-epics-cmds",
        statustopic="forward-epics-status",
        instpvtopic="amor-pvs",
        instpvschema='f142',
        brokers=["localhost:9092"],
    ),

    NexusDataSink=device(
        'nicos_ess.devices.datasinks.nexussink.NexusFileWriterSink',
        description="Sink for NeXus file writer (kafka-to-nexus)",
        brokers=["localhost:9092"],
        cmdtopic="file-writer-cmds",
        status_provider='NexusFileWriter',
        templatesmodule='nicos_sinq.amor.nexus.nexus_templates',
        templatename='amor_default'
    ),

    HistogramDataSink=device(
        'nicos_sinq.amor.devices.datasinks.ImageKafkaWithLiveViewDataSink',
        brokers=["localhost:9092"],
        channeltostream={
            'area_detector_channel': ('AMOR.detector.area', 'area.tof'),
            'single_det1_channel': ('AMOR.detector.single1', 'single.tof'),
            'single_det2_channel': ('AMOR.detector.single2', 'single.tof'),
            'single_det3_channel': ('AMOR.detector.single3', 'single.tof'),
        },
    ),

    NexusFileWriter=device(
        'nicos_ess.devices.datasinks.nexussink.NexusFileWriterStatus',
        description="Status for nexus file writing",
        brokers=["localhost:9092"],
        statustopic="file-writer-status",
    )
)
