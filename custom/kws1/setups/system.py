description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email'],
)

includes = ['notifiers']

modules = ['commands.standard']

devices = dict(
    KWS1     = device('devices.instrument.Instrument',
                      description = 'KWS-1 instrument',
                      instrument = 'KWS-1',
                      doi = 'http://dx.doi.org/10.17815/jlsrf-1-26',
                      responsible = 'H. Frielinghaus <h.frielinghaus@fz-juelich.de>',
                     ),

    Sample   = device('devices.sample.Sample',
                      description = 'Sample object',
                     ),

    Exp      = device('devices.experiment.Experiment',
                      description = 'experiment object',
                      dataroot = '/data',
                      sendmail = True,
                      serviceexp = '0',
                      sample = 'Sample',
                     ),

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
                      path = None,
                      minfree = 5,
                     ),
)
