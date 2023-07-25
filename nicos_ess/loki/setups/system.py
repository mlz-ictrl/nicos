description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument='LoKI',
    experiment='Exp',
    datasinks=['conssink', 'liveview', 'daemonsink'],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands']

KAFKA_BROKERS = ["10.100.1.19:8093"]

devices = dict(
    LoKI=device(
        'nicos.devices.instrument.Instrument',
        description='instrument object',
        instrument='LoKI',
        responsible='J. Houston <judith.houston@ess.eu>',
        website='https://europeanspallationsource.se/instruments/loki'),
    Sample=device(
        'nicos_ess.devices.sample.EssSample',
        description='The currently used sample',
    ),
    Exp=device(
        'nicos_ess.devices.experiment.EssExperiment',
        description='experiment object',
        dataroot='/opt/nicos-data',
        filewriter_base='loki',
        sample='Sample',
        cache_filepath='/opt/nicos-data/loki/cached_proposals.json'),
    conssink=device(
        'nicos_ess.devices.datasinks.console_scan_sink.ConsoleScanSink'),
    daemonsink=device('nicos.devices.datasinks.DaemonSink', ),
    liveview=device('nicos.devices.datasinks.LiveViewSink', ),
    KafkaForwarderStatus=device(
        'nicos_ess.devices.forwarder.EpicsKafkaForwarder',
        description='Monitors the status of the Forwarder',
        statustopic="loki_forwarder_status",
        brokers=KAFKA_BROKERS,
    ),
    SciChat=device(
        'nicos_ess.devices.scichat.ScichatBot',
        description='Sends messages to SciChat',
        brokers=KAFKA_BROKERS,
    ),
)
