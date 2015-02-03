description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'nectarhw.nectar.frm2',
    instrument = 'Instrument',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.basic', 'nicos.commands.standard', 'nicos.commands.imaging']

devices = dict(
    Sample   = device('devices.sample.Sample'),

    Exp      = device('frm2.experiment.ImagingExperiment',
                      dataroot = '/data',
                      propdb = '/etc/propdb',
                      serviceexp = 'service',
                      sample = 'Sample',
                      mailsender = 'nectar@frm2.tum.de',
                      sendmail = False,
                      zipdata = False,
                      managerights = {},
                      localcontact = 'Dr. Stefan Soellradl '\
                                    '<stefan.soellradl@frm2.tum.de>',
                     ),

    Instrument = device('devices.instrument.Instrument',
                        description = 'NECTAR instrument',
                        instrument = 'NECTAR',
                        responsible = 'Dr. Stefan Soellradl',
                       ),

    filesink = device('devices.datasinks.AsciiDatafileSink'),

    conssink = device('devices.datasinks.ConsoleSink'),

    daemonsink = device('devices.datasinks.DaemonSink'),

    Space    = device('devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      path = None,
                      minfree = 5,
                     ),

    # Configure source and copy addresses to an existing address.
    email    = device('devices.notifiers.Mailer',
                      sender = 'nectar@frm2.tum.de',
                      copies = [('stefan.soellradl@frm2.tum.de', 'all')],
                      subject = '[NICOS]',
                      mailserver = 'smtp.frm2.tum.de',
                     ),

    # Configure SMS receivers if wanted and registered with IT.
    smser    = device('devices.notifiers.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = [],
                     ),
)
