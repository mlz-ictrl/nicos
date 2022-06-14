description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument='E03',
    experiment='Exp',
    datasinks=['conssink', 'daemonsink'],
)

modules = ['nicos.commands.standard', 'nicos_ess.commands']

devices = dict(
    E03=device(
        'nicos.devices.instrument.Instrument',
        description='instrument object',
        instrument='E03',
        responsible='A. Pettersson <a.pettersson@ess.eu>',
    ),
    Sample=device(
        'nicos.devices.sample.Sample',
        description='The currently used sample',
    ),
    Exp=device(
        'nicos.devices.experiment.Experiment',
        description='experiment object',
        dataroot='/opt/nicos-data',
        sendmail=True,
        serviceexp='p0',
        sample='Sample',
    ),
    conssink=device(
        'nicos_ess.devices.datasinks.console_scan_sink.ConsoleScanSink'),
    daemonsink=device('nicos.devices.datasinks.DaemonSink', ),
    Space=device(
        'nicos.devices.generic.FreeSpace',
        description='The amount of free space for storing data',
        path=None,
        minfree=5,
    ),
)
