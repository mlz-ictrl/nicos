description = 'system setup only'
group = 'lowlevel'

sysconfig = dict(
    cache = 'mira1',
    instrument = 'mira',
    experiment = 'Exp',
    notifiers = ['email', 'smser'],
    datasinks = ['conssink', 'filesink', 'dmnsink', 'gracesink'],
)

devices = dict(
    email    = device('devices.notifiers.Mailer',
                      sender = 'nicos@mira1',
                      copies = ['rgeorgii@frm2.tum.de'],
                      subject = 'MIRA'),

    smser    = device('devices.notifiers.SMSer',
                      server = 'triton.admin.frm2'),

    Exp      = device('mira.experiment.MiraExperiment',
                      sample = 'Sample',
                      dataroot = '/data',
                      propdb = 'useroffice@tacodb.taco.frm2:useroffice'),

    Sample   = device('devices.experiment.Sample'),

    mira     = device('devices.instrument.Instrument',
                      instrument = 'MIRA',
                      responsible = 'Robert Georgii <robert.georgii@frm2.tum.de>'),

    filesink = device('devices.datasinks.AsciiDatafileSink',
                      semicolon = False),

    conssink = device('devices.datasinks.ConsoleSink'),

    dmnsink  = device('devices.datasinks.DaemonSink'),

    gracesink= device('devices.datasinks.GraceSink'),
)
