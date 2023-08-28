description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument='MIRACLES',
    experiment='Exp',
    datasinks=['conssink', 'daemonsink', 'liveview'],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands']

devices = dict(
    MIRACLES=device(
        'nicos.devices.instrument.Instrument',
        description='instrument object',
        instrument='MIRACLES',
        responsible='A Person <a.person@ess.eu>',
        website='https://europeanspallationsource.se/instruments/miracles'),
    Sample=device(
        'nicos_ess.devices.sample.EssSample',
        description='The currently used sample',
    ),
    Exp=device(
        'nicos_ess.devices.experiment.EssExperiment',
        description='experiment object',
        dataroot='/opt/nicos-data',
        sample='Sample',
        cache_filepath='/opt/nicos-data/cached_proposals.json'),
    conssink=device(
        'nicos_ess.devices.datasinks.console_scan_sink.ConsoleScanSink'),
    daemonsink=device('nicos.devices.datasinks.DaemonSink', ),
    liveview=device('nicos.devices.datasinks.LiveViewSink', ),
)
