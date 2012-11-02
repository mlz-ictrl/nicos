description = 'NICOS system setup'

sysconfig = dict(
    cache = 'cpci1.toftof.frm2',
    instrument = 'TOFTOF',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['emailer', 'smser'],
)

devices = dict(
    TOFTOF   = device('devices.instrument.Instrument',
                      instrument = 'TOFTOF'),

    Sample   = device('devices.experiment.Sample'),

    Exp      = device('devices.experiment.Experiment',
                      dataroot = '/users/data',
                      sample = 'Sample',
                      localcontact = 'M. Mustermann',
                      elog = False),

    filesink = device('devices.datasinks.AsciiDatafileSink',
                      prefix = '/users/data'),

    conssink = device('devices.datasinks.ConsoleSink'),

    daemonsink = device('devices.datasinks.DaemonSink'),

    emailer  = device('devices.notifiers.Mailer',
                      sender = 'nicos@cpci1.toftof.frm2',
                      copies = [],
                      subject = 'TOFTOF'),

    smser    = device('devices.notifiers.SMSer',
                      server = 'triton.admin.frm2'),

    Space    = device('devices.generic.FreeSpace',
                      path = '/users',
                      minfree = 5),
)
