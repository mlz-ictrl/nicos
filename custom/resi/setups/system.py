description = 'system setup only'
group = 'basic'

sysconfig = dict(
    cache = 'resictrl.resi.frm2',
    instrument = 'resiInstrument',
    experiment = 'Exp',
    notifiers = ['email'],
    datasinks = ['conssink', 'filesink', 'dmnsink'],
)

includes = ['notifiers']

modules = ['nicos.commands.standard']

devices = dict(
    Exp = device('resi.experiment.ResiExperiment',
                 description = 'The currently running experiment',
                 sample = 'Sample',
                 dataroot = '/data/data6/',
                ),

    resiInstrument = device('devices.instrument.Instrument',
                            description = 'Thermal neutron single crystal '
                                          'diffractometer',
                            instrument = 'RESI',
                            doi = 'http://dx.doi.org/10.17815/jlsrf-1-23',
                            responsible = 'B. Pedersen <bjoern.pedersen@frm2.tum.de>'),

    Sample = device('devices.sample.Sample',
                    description = 'The sample',
                   ),

    filesink = device('devices.datasinks.AsciiScanfileSink',
                      lowlevel = True,
                     ),

    conssink = device('devices.datasinks.ConsoleScanSink',
                      lowlevel = True,
                     ),

    dmnsink = device('devices.datasinks.DaemonSink',
                     lowlevel = True,
                    ),
)
