description = 'system setup only'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'DEL',
    experiment = 'Exp',
    notifiers = ['email', ],
    datasinks = ['conssink', 'filesink', 'dmnsink'],
)

modules = ['commands.standard', 'commands.taco']

includes = ['notifiers', ]

devices = dict(
    Exp      = device('devices.experiment.Experiment',
                      description = 'experiment object',
                      sample = 'Sample',
                      dataroot = '/localdata/nicos',
                      serviceexp = '0',
                      sendmail = True,
                      mailsender = 'karl.zeitelhack@frm2.tum.de',
                     ),

    Sample   = device('devices.sample.Sample',
                      description = 'currently used sample',
                     ),

    DEL      = device('devices.instrument.Instrument',
                      description = 'instrument object',
                      instrument = 'DEL',
                      responsible = 'Karl Zeitelhack <karl.zeitelhack@frm2.tum.de>',
                     ),

    filesink = device('devices.datasinks.AsciiScanfileSink',
                      semicolon = False,
                      lowlevel = True,
                     ),

    conssink = device('devices.datasinks.ConsoleScanSink',
                      lowlevel = True,
                     ),

    dmnsink  = device('devices.datasinks.DaemonSink',
                      lowlevel = True,
                     ),

    Space    = device('devices.generic.FreeSpace',
                      description = 'free space for data files',
                      path = '/localdata/nicos',
                      minfree = 10,
                     ),
)
