description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email'],
)

modules = ['commands.standard']

devices = dict(
    KWS1     = device('devices.instrument.Instrument',
                      description = 'KWS-1 instrument',
                      instrument = 'KWS-1',
                      responsible = 'H. Frielinghaus <h.frielinghaus@fz-juelich.de>',
                     ),

    Sample   = device('devices.sample.Sample',
                      description = 'Sample object',
                     ),

    Exp      = device('devices.experiment.Experiment',
                      description = 'experiment object',
                      dataroot = 'data',
                      sendmail = True,
                      serviceexp = '0',
                      sample = 'Sample',
                     ),

    filesink = device('devices.datasinks.AsciiDatafileSink',
                      lowlevel = True,
                     ),

    conssink = device('devices.datasinks.ConsoleSink',
                      lowlevel = True,
                     ),

    daemonsink = device('devices.datasinks.DaemonSink',
                        lowlevel = True,
                       ),

    Space    = device('devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      path = None,
                      minfree = 5,
                     ),

    # Configure source and copy addresses to an existing address.
    email    = device('devices.notifiers.Mailer',
                      sender = 'kws1@frm2.tum.de',
                      copies = [('g.brandl@fz-juelich.de', 'all'),   # for now
                               ],
                      subject = '[KWS-1]',
                      lowlevel = True,
                     ),

    # Configure SMS receivers if wanted and registered with IT.
    smser    = device('devices.notifiers.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = [],
                      lowlevel = True,
                     ),
)
