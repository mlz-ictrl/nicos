description = 'system setup'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'POLI',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['commands.standard', 'poli.commands']

devices = dict(
    POLI     = device('devices.instrument.Instrument',
                      description = 'The POLI instrument',
                      responsible = 'V. Hutanu <vladimir.hutanu@frm2.tum.de>',
                      instrument = 'POLI',
                      doi = 'http://dx.doi.org/10.17815/jlsrf-1-22',
                     ),

    Sample   = device('devices.sample.Sample',
                      description = 'The current used sample',
                     ),

    # Configure dataroot here (usually /data).
    Exp      = device('frm2.experiment.Experiment',
                      description = 'experiment object',
                      dataroot = '/data',
                      managerights = dict(enableDirMode=0o775,
                                          enableFileMode=0o644,
                                          disableDirMode=0o750,
                                          disableFileMode=0o440,
                                          enableOwner='jcns',
                                          enableGroup='games',
                                          disableOwner='jcns',
                                          disableGroup='poli',
                                         ),
                      sendmail = True,
                      serviceexp = 'p0',
                      sample = 'Sample',
                      propdb = '/home/jcns/.propdb',
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
                      path = '/home/jcns/data',
                      minfree = 5,
                     ),

    # Configure source and copy addresses to an existing address.
    email    = device('devices.notifiers.Mailer',
                      sender = 'vladimir.hutanu@frm2.tum.de',
                      copies = [('vladimir.hutanu@frm2.tum.de', 'all'),
                                ('andrew.sazonov@frm2.tum.de', 'all'),
                                ('alerts.sw.zea2@fz-juelich.de', 'important'),
                               ],
                      subject = 'NICOS',
                      mailserver = 'mailhost.frm2.tum.de',
                      lowlevel = True,
                     ),

    # Configure SMS receivers if wanted and registered with IT.
    smser    = device('devices.notifiers.SMSer',
                      server = 'triton.admin.frm2',
                      receivers = [],
                      lowlevel = True,
                     ),
)
