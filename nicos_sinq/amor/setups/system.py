description = 'system setup'

display_order = 18

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'Amor',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink', 'syncdaqsink', 'scansink'],
    )

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
    Exp = device('nicos_sinq.amor.devices.experiment.AmorExperiment',
                 description = 'experiment object',
                 dataroot = configdata('config.DATA_PATH'),
                 scriptroot = configdata('config.SCRIPT_ROOT'),
                 sample = 'Sample',
                 ),
    Space = device('nicos.devices.generic.FreeSpace',
                   description = 'The amount of free space for storing data',
                   path = None,
                   minfree = 5,
                   visibility = (),
                   ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    scansink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    syncdaqsink = device('nicos_sinq.amor.devices.datasinks.SyncDaqSink',
                         description = 'Sink for synchronizing the DAQ PC and the ring modules at the start of each measurement'
                         ),
    )
