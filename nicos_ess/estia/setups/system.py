description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache='localhost',
    instrument='ESTIA',
    experiment='Exp',
    datasinks=['conssink', 'filesink', 'daemonsink'],
)

modules = ['nicos.commands.standard']

includes = ['temp']

devices = dict(
    ESTIA=device('nicos.devices.instrument.Instrument',
                 description='instrument object',
                 instrument='estia',
                 responsible='Artur Glavic <artur.glavic@psi.ch>',
                 website='https://confluence.esss.lu.se/display/ESTIA',
                 operators=['ESS', 'PSI'],
                 facility='Paul Scherrer Institut (PSI)',
                 ),

    Sample=device('nicos.devices.sample.Sample',
                  description='The currently used sample',
                  ),

    Exp=device('nicos.devices.experiment.Experiment',
               description='experiment object',
               dataroot='/opt/nicos-data',
               sendmail=True,
               serviceexp='p0',
               sample='Sample',
               ),

    filesink=device('nicos.devices.datasinks.AsciiScanfileSink',
                    ),

    conssink=device('nicos.devices.datasinks.ConsoleScanSink',
                    ),

    daemonsink=device('nicos.devices.datasinks.DaemonSink',
                      ),

    Space=device('nicos.devices.generic.FreeSpace',
                 description='The amount of free space for storing data',
                 path='/opt/nicos-data',
                 minfree=5,
                 ),
)
