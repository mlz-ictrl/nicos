description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument='ODIN',
    experiment='Exp',
    datasinks=['conssink', 'daemonsink', 'liveview'],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands']

devices = dict(
    ODIN=device(
        'nicos.devices.instrument.Instrument',
        description='instrument object',
        instrument='ODIN',
        responsible='Manuel Morgano <manuel.morgano@ess.eu>',
        website='https://europeanspallationsource.se/instruments/odin'),
    Sample=device(
        'nicos.devices.sample.Sample',
        description='The currently used sample',
    ),
    Exp=device(
        'nicos_ess.devices.experiment.EssExperiment',
        description='experiment object',
        dataroot='/opt/nicos-data',
        filewriter_root='/opt/nicos-data/odin',
        sample='Sample',
        cache_filepath='/opt/nicos-data/odin/cached_proposals.json'),
    conssink=device(
        'nicos_ess.devices.datasinks.console_scan_sink.ConsoleScanSink'),
    daemonsink=device('nicos.devices.datasinks.DaemonSink', ),
    liveview=device('nicos.devices.datasinks.LiveViewSink', ),
)
