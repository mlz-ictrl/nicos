description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email'],
)

modules = ['nicos.commands.standard']

devices = dict(
    KWS2     = device('devices.instrument.Instrument',
                      description = 'KWS-2 instrument',
                      instrument = 'KWS-2',
                      doi = 'http://dx.doi.org/10.17815/jlsrf-1-27',
                      responsible = 'A. Radulescu <a.radulescu@fz-juelich.de>',
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

    filesink = device('devices.datasinks.AsciiScanfileSink',
                      lowlevel = True,
                     ),

    conssink = device('devices.datasinks.ConsoleScanSink',
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
                      sender = 'kws2@frm2.tum.de',
                      copies = [('g.brandl@fz-juelich.de', 'all'),   # for now
                               ],
                      subject = '[KWS-2]',
                      lowlevel = True,
                     ),

    # Configure SMS receivers if wanted and registered with IT.
    smser    = device('devices.notifiers.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = [],
                      lowlevel = True,
                     ),
)
