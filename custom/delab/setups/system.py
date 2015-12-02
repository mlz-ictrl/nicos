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
                      sample = 'Sample',
                      dataroot = '/localdata/nicos',
                      serviceexp = '0',
                      sendmail = True,
                      mailsender = 'karl.zeitelhack@frm2.tum.de',
                     ),

    Sample   = device('devices.sample.Sample'),

    DEL     = device('devices.instrument.Instrument',
                     instrument = 'DEL',
                     responsible = 'Karl Zeitelhack <karl.zeitelhack@frm2.tum.de>',
                    ),

    filesink = device('devices.datasinks.AsciiDatafileSink',
                      semicolon = False,
                     ),

    conssink = device('devices.datasinks.ConsoleSink'),

    dmnsink  = device('devices.datasinks.DaemonSink'),

    Space    = device('devices.generic.FreeSpace',
                      path = '/localdata/nicos',
                      minfree = 10,
                     ),
)
