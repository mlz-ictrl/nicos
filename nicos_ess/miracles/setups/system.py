description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument='MIRACLES',
    experiment='Exp',
    datasinks=['conssink', 'daemonsink', 'liveview'],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands.epics']

devices = dict(
    MIRACLES=device(
        'nicos.devices.instrument.Instrument',
        description='instrument object',
        instrument='MIRACLES',
        responsible='A Person <a.person@ess.eu>',
        website='https://europeanspallationsource.se/instruments/miracles'
    ),

    Sample=device(
        'nicos.devices.sample.Sample',
        description='The currently used sample',
    ),

    Exp=device(
        'nicos_ess.devices.experiment.EssExperiment',
        description='experiment object',
        dataroot='/opt/nicos-data',
        sendmail=False,
        serviceexp='p0',
        sample='Sample',
        server_url='https://useroffice-test.esss.lu.se/graphql',
        instrument='MIRACLES'
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
)

startupcode = '''
'''
