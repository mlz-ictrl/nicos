description = 'system setup'

display_order = 18

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'Amor',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink', 'syncdaqsink'],
    )

# Commented out on 27.11.2024 (Stefan Mathis). To be checked in shutdown - is this ever needed?
#  'nicos_ess.commands.filewriter',
modules = [
    'nicos.commands.standard',
    'nicos_sinq.amor.commands',
    'nicos_sinq.commands.sics',
    'nicos_sinq.commands.epicscommands',
]

devices = dict(
    Amor = device('nicos.devices.instrument.Instrument',
                  description = 'instrument object',
                  instrument = 'SINQ AMOR',
                  responsible = 'Jochen Stahn <jochen.stahn@psi.ch>',
                  operators = ['Paul-Scherrer-Institut (PSI)'],
                  facility = 'SINQ, PSI',
                  website = 'https://www.psi.ch/sinq/amor/amor'
                  ),
    Sample = device('nicos_sinq.amor.devices.sample.AmorSample',
                    description = 'The currently used sample',
                    ),
    Exp = device('nicos_sinq.devices.experiment.SinqExperiment',
                 description = 'experiment object',
                 dataroot = configdata('config.DATA_PATH'),
                 sample = 'Sample',
                 ),
    Space = device('nicos.devices.generic.FreeSpace',
                   description = 'The amount of free space for storing data',
                   path = None,
                   minfree = 5,
                   visibility = (),
                   ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    syncdaqsink = device('nicos_sinq.amor.devices.datasinks.SyncDaqSink',
                         description = 'Sink for synchronizing the DAQ PC and the ring modules at the start of each measurement'
                         ),
    )
