description = 'system setup only'
group = 'lowlevel'

sysconfig = dict(
    cache = 'mira1',
    instrument = 'mira',
    experiment = 'Exp',
    notifiers = ['email', 'smser'],
    datasinks = ['conssink', 'filesink', 'dmnsink', 'gracesink'],
)

modules = ['nicos.commands.standard', 'nicos.commands.taco']

devices = dict(
    email    = device('devices.notifiers.Mailer',
                      sender = 'rgeorgii@frm2.tum.de',
                      copies = ['rgeorgii@frm2.tum.de', 'klaus.seemann@frm2.tum.de'],
                      subject = 'MIRA'),

    smser    = device('devices.notifiers.SMSer',
                      server = 'triton.admin.frm2'),

    Exp      = device('mira.experiment.MiraExperiment',
                      sample = 'Sample',
                      dataroot = '/data',
                      serviceexp = '0',
                      propprefix = '',
                      sendmail = True,
                      localcontact = 'R. Georgii <rgeorgii@frm2.tum.de>',
                      mailsender = 'rgeorgii@frm2.tum.de',
                      propdb = '/etc/proposaldb'),

    Sample   = device('devices.sample.Sample'),

    mira     = device('devices.instrument.Instrument',
                      instrument = 'MIRA',
                      responsible = 'Robert Georgii <robert.georgii@frm2.tum.de>'),

    filesink = device('devices.datasinks.AsciiDatafileSink',
                      semicolon = False),

    conssink = device('devices.datasinks.ConsoleSink'),

    dmnsink  = device('devices.datasinks.DaemonSink'),

    gracesink= device('devices.datasinks.GraceSink'),

    Space    = device('devices.generic.FreeSpace',
                      path = '/data',
                      minfree = 10),
)

