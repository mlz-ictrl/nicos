description = 'NICOS system setup'

sysconfig = dict(
    cache = 'tasgroup2.taco.frm2',
    instrument = 'SE',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['emailer', 'smser'],
)

devices = dict(
    SE   = device('nicos.instrument.Instrument',
                      instrument = 'SE'),

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
                      sender = 'nicos@tasgroup2.taco.frm2',
                      copies = [],
                      subject = 'SE'),

    smser    = device('nicos.notify.SMSer',
                      server = 'triton.admin.frm2'),

    Space    = device('nicos.generic.FreeSpace',
                      description = 'The free space on the data storage', 
                      path = '/',
                      minfree = 5),
)
