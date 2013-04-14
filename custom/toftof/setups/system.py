description = 'NICOS system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'tofhw.toftof.frm2',
    instrument = 'TOFTOF',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['emailer', 'smser'],
)

modules = ['nicos.commands.standard']

devices = dict(
    TOFTOF   = device('devices.instrument.Instrument',
                      responsible = 'W. Lohstroh <wiebke.lohstroh@frm2.tum.de>, ' \
                                    'G. Simeoni <giovanna.simeoni@frm2.tum.de>',
                      instrument = 'TOFTOF'),

    Sample   = device('devices.experiment.Sample'),

    Exp      = device('frm2.experiment.Experiment',
                      dataroot = '/users/data',
                      sample = 'Sample',
                      localcontact = 'W. Lohstroh, G. Simeoni',
                      serviceexp = '0',
                      sendmail = True,
                      mailsender = 'nicos.toftof@frm2.tum.de',
                      propdb = '/opt/nicos/setups/userdb',
                      elog = True),

    filesink = device('devices.datasinks.AsciiDatafileSink'),

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
