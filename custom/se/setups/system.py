description = 'NICOS system setup'

sysconfig = dict(
    cache = 'tasgroup2.taco.frm2',
    instrument = 'SE',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['emailer', 'smser'],
)

devices = dict(
    SE   = device('devices.instrument.Instrument',
                      instrument = 'SE'),

    Sample   = device('devices.experiment.Sample'),

    Exp      = device('devices.experiment.Experiment',
                      dataroot = '/users/data',
                      sample = 'Sample',
                      elog = False),

    filesink = device('devices.datasinks.AsciiDatafileSink',
                      prefix = 'data'),

    conssink = device('devices.datasinks.ConsoleSink'),

    daemonsink = device('devices.datasinks.DaemonSink'),

    emailer  = device('devices.notifiers.Mailer',
                      sender = 'nicos@tasgroup2.taco.frm2',
                      copies = [],
                      subject = 'SE'),

    smser    = device('devices.notifiers.SMSer',
                      server = 'triton.admin.frm2'),

    Space    = device('devices.generic.FreeSpace',
                      description = 'The free space on the data storage', 
                      path = '/',
                      minfree = 5),
)
