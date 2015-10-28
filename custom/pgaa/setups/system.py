description = 'system setup'

sysconfig = dict(
    cache = 'tequila.pgaa.frm2',
    instrument = 'PGAA',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser', ],
)

modules = ['commands.standard']

includes = ['notifiers', ]

devices = dict(
    Sample   = device('devices.sample.Sample',
                      description = 'The sample',
                     ),

    PGAA = device('devices.instrument.Instrument',
                  description = 'Prompt gamma and in-beam neutron activation '
                                'analysis facility',
                  doi = 'http://dx.doi.org/10.17815/jlsrf-1-46',
                  responsible = 'Dr. Zsolt Revay <zsolt.revay@frm2.tum.de>',
                 ),

    Exp      = device('devices.experiment.Experiment',
                      description = 'The currently running experiment',
                      dataroot = '/localdata/',
                      sample = 'Sample'),

    filesink = device('devices.datasinks.AsciiScanfileSink',
                      lowlevel = True,
                     ),

    conssink = device('devices.datasinks.ConsoleScanSink',
                      lowlevel = True,
                     ),

    daemonsink = device('devices.datasinks.DaemonSink',
                        lowlevel = True,
                       ),

    Space    = device('devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      minfree = 0.5,
                      path = None,
                     ),
)
