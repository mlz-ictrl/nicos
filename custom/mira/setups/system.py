description = 'system setup only'
group = 'lowlevel'

sysconfig = dict(
    cache = 'mira1',
    instrument = 'mira',
    experiment = 'Exp',
    notifiers = ['email', 'smser'],
    datasinks = ['conssink', 'filesink', 'dmnsink'],
)

modules = ['commands.standard', 'commands.taco']

includes = ['notifiers', ]

devices = dict(
    Exp      = device('mira.experiment.MiraExperiment',
                      description = 'experiment object',
                      sample = 'Sample',
                      dataroot = '/data',
                      serviceexp = '0',
                      propprefix = '',
                      sendmail = True,
                      mailsender = 'rgeorgii@frm2.tum.de',
                      propdb = '/etc/proposaldb',
                     ),

    Sample   = device('devices.sample.Sample',
                      description = 'sample object',
                     ),

    mira     = device('devices.instrument.Instrument',
                      description = 'instrument object',
                      instrument = 'MIRA',
                      doi = 'http://dx.doi.org/10.17815/jlsrf-1-21',
                      responsible = 'Robert Georgii <robert.georgii@frm2.tum.de>',
                     ),

    filesink = device('devices.datasinks.AsciiDatafileSink',
                      semicolon = False,
                      lowlevel = True,
                     ),

    conssink = device('devices.datasinks.ConsoleSink',
                      lowlevel = True,
                     ),

    dmnsink  = device('devices.datasinks.DaemonSink',
                      lowlevel = True,
                     ),

    Space    = device('devices.generic.FreeSpace',
                      description = 'free space on data share',
                      path = '/data',
                      minfree = 10,
                     ),
)
