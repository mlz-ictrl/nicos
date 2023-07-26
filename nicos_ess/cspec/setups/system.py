description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument=None,
    experiment='Exp',
    datasinks=['conssink', 'daemonsink', 'liveview'],
    notifiers=['email'],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands']

includes = [
    'notifiers',
]

devices = dict(
    cspec=device(
        'nicos.devices.instrument.Instrument',
        description='CSPEC instrument',
        facility='European Spallation Source (ESS)',
        instrument='CSPEC',
        responsible='P.P. Deen <pascale.deen@esss.se>',
        website='https://europeanspallationsource.se/instruments/cspec',
        operators=[
            'European Spallation Source (ESS)',
            'Technische Universität München (TUM)',
        ]),
    Sample=device(
        'nicos_ess.devices.sample.EssSample',
        description='The currently used sample',
    ),
    Exp=device('nicos_ess.devices.experiment.EssExperiment',
               description='experiment object',
               dataroot='/opt/nicos-data',
               sample='Sample',
               cache_filepath='/opt/nicos-data/cspec/cached_proposals.json'),
    conssink=device(
        'nicos_ess.devices.datasinks.console_scan_sink.ConsoleScanSink'),
    daemonsink=device(
        'nicos.devices.datasinks.DaemonSink',
        visibility=(),
    ),
    liveview=device('nicos.devices.datasinks.LiveViewSink', ),
)
