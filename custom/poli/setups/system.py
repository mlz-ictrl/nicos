description = 'system setup'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'POLI',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard', 'poli.commands']

includes = ['notifiers', 'table', 'mono', 'slits', 'reactor', 'shutter']

devices = dict(
    POLI     = device('nicos.devices.sxtal.instrument.LiftingSXTal',
                      description = 'The POLI instrument',
                      responsible = 'V. Hutanu <vladimir.hutanu@frm2.tum.de>',
                      instrument = 'POLI',
                      doi = 'http://dx.doi.org/10.17815/jlsrf-1-22',
                      mono = 'wavelength',
                      gamma = 'gamma',
                      omega = 'sth',
                      nu = 'liftingctr',
                     ),

    Sample   = device('nicos.devices.sxtal.sample.SXTalSample',
                      description = 'The currently used sample',
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
                      mailsender = 'poli@frm2.tum.de',
                      serviceexp = 'p0',
                      sample = 'Sample',
                      propdb = '/home/jcns/.propdb',
                     ),

    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
                      lowlevel = True,
                     ),

    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
                      lowlevel = True,
                     ),

    daemonsink = device('nicos.devices.datasinks.DaemonSink',
                        lowlevel = True,
                       ),

    Space    = device('nicos.devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      path = '/home/jcns/data',
                      minfree = 5,
                     ),
)

extended = dict(
    poller_cache_reader = ['liftingctr']
)
