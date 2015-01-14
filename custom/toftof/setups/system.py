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
                      description = 'The famous TOFTOF instrument',
                      responsible = 'W. Lohstroh <wiebke.lohstroh@frm2.tum.de>, ' \
                                    'G. Simeoni <giovanna.simeoni@frm2.tum.de>',
                      instrument = 'TOFTOF',
                     ),

    Sample   = device('devices.sample.Sample',
                      description = 'The current used sample',
                     ),

    Exp      = device('frm2.experiment.Experiment',
                      description = 'The current running experiment',
                      dataroot = '/users/data',
                      sample = 'Sample',
                      localcontact = 'W. Lohstroh, G. Simeoni',
                      serviceexp = '0',
                      propprefix = '',
                      sendmail = True,
                      mailsender = 'nicos.toftof@frm2.tum.de',
                      propdb = '/opt/nicos/propdb',
                      managerights = dict(enableDirMode=0o775,
                                          enableFileMode=0o664,
                                          disableDirMode=0o550,
                                          disableFileMode=0o440,
                                          owner='nicd', group='nicd',
                                         ),
                      elog = True,
                      scancounter = 'scancounter',
                      # filecounter = '/users/data/counter',
                      imagecounter = 'counter',
                     ),

    filesink = device('devices.datasinks.AsciiDatafileSink'),

    conssink = device('devices.datasinks.ConsoleSink'),

    daemonsink = device('devices.datasinks.DaemonSink'),

    emailer  = device('devices.notifiers.Mailer',
                      description = 'Notifier service to send emails',
                      sender = 'nicos.toftof@frm2.tum.de',
                      copies = ['wiebke.lohstroh@frm2.tum.de',
                                'giovanna.simeoni@frm2.tum.de'],
                      subject = 'TOFTOF',
                     ),

    smser    = device('devices.notifiers.SMSer',
                      description = 'Notifier service to send SMS',
                      server = 'triton.admin.frm2',
                     ),

    Space    = device('devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      path = '/users',
                      minfree = 5,
                     ),
)
