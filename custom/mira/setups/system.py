name = 'system setup only'

devices = dict(
    System   = device('nicos.system.System',
                      cache = 'Cache',
                      notifiers = ['email', 'smser'],
                      datasinks = ['conssink', 'filesink', 'dmnsink', 'gracesink'],
                      instrument = 'mira',
                      experiment = 'Exp'),

    email    = device('nicos.notify.Mailer',
                      sender = 'nicos@mira1',
                      copies = ['rgeorgii@frm2.tum.de'],
                      subject = 'MIRA'),

    smser    = device('nicos.notify.SMSer',
                      server='triton.admin.frm2'),

    Exp      = device('nicos.mira.experiment.MiraExperiment',
                      sample = 'Sample',
                      datapath = ['/data/testdata']),

    filesink = device('nicos.data.AsciiDatafileSink',
                      prefix = 'data'),

    conssink = device('nicos.data.ConsoleSink'),

    dmnsink  = device('nicos.data.DaemonSink'),

    gracesink= device('nicos.data.GraceSink'),

    Cache    = device('nicos.cache.client.CacheClient',
                      lowlevel = True,
                      server = 'mira1',
                      prefix = 'nicos/'),
)
