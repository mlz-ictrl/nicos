description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Spheres = device('nicos.devices.instrument.Instrument',
                      description = 'SPHERES instrument object',
                      instrument = 'SPHERES',
                     doi = 'http://dx.doi.org/10.17815/jlsrf-1-38',
                      responsible = 'Michaela Zamponi <m.zamponi@fz-juelich.de>',
                     ),

    Sample   = device('nicos.devices.sample.Sample',
                      description = 'The current used sample',
                     ),

    Exp      = device('nicos.devices.experiment.Experiment',
                      description = 'experiment object',
                      dataroot = '/home/jcns/nicos-data',
                      sendmail = True,
                      serviceexp = 'service',
                      sample = 'Sample',
                     ),

    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
                      lowlevel = True,
                     ),

    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
                      lowlevel = True,
                     ),

    daemonsink = device('nicos.devices.datasinks.DaemonSink',
                        lowlevel = True,
                       ),

    Space    = device('nicos.devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      path = None,
                      minfree = 5,
                     ),
)
