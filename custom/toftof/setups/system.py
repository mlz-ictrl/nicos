description = 'NICOS system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'tofhw.toftof.frm2',
    instrument = 'TOFTOF',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['emailer', 'smser'],
)

devices = dict(
    TOFTOF   = device('devices.instrument.Instrument',
                      instrument = 'TOFTOF'),

    Sample   = device('devices.experiment.Sample'),

    Exp      = device('frm2.experiment.Experiment',
                      dataroot = '/users/data',
                      responsible = 'W. Lohstroh <wiebke.lohstroh@frm2.tum.de>, ' \
                                    'G. Simeoni <giovanna.simeoni@frm2.tum.de>',
                      sample = 'Sample',
                      localcontact = 'W. Lohstroh, G. Simeoni',
                      serviceexp = '0',
                      sendmail = True,
                      mailsender = 'nicos.toftof@frm2.tum.de',
                      propdb = 'useroffice@tacodb.taco.frm2:useroffice',
                      elog = True),

    filesink = device('devices.datasinks.AsciiDatafileSink',
                      prefix = '/users/data'),

    conssink = device('devices.datasinks.ConsoleSink'),

    daemonsink = device('devices.datasinks.DaemonSink'),

    emailer  = device('devices.notifiers.Mailer',
                      sender = 'nicos.toftof@frm2.tum.de',
                      copies = ['wiebke.lohstroh@frm2.tum.de',
                                'giovanna.simeoni@frm2.tum.de'],
                      subject = 'TOFTOF'),

    smser    = device('devices.notifiers.SMSer',
                      server = 'triton.admin.frm2'),

    Space    = device('devices.generic.FreeSpace',
                      path = '/users',
                      minfree = 5),
)
