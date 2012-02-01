description = 'NICOS system setup'

sysconfig = dict(
    cache = 'cpci1.toftof.frm2',
    instrument = 'TOFTOF',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['emailer', 'smser'],
)

devices = dict(
    TOFTOF   = device('nicos.instrument.Instrument',
                      instrument = 'TOFTOF'),

    Sample   = device('nicos.experiment.Sample'),

    Exp      = device('nicos.experiment.Experiment',
                      dataroot = '/users/data',
                      sample = 'Sample',
                      elog = False),

    filesink = device('nicos.data.AsciiDatafileSink',
                      prefix = 'data'),

    conssink = device('nicos.data.ConsoleSink'),

    daemonsink = device('nicos.data.DaemonSink'),

    emailer  = device('nicos.notify.Mailer',
                      sender = 'nicos@cpci1.toftof.frm2',
                      copies = [],
                      subject = 'TOFTOF'),

    smser    = device('nicos.notify.SMSer',
                      server = 'triton.admin.frm2'),

    Space    = device('nicos.generic.FreeSpace',
                      path = '/users',
                      minfree = 5),
)
