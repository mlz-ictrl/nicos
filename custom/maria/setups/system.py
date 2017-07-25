description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'maria',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['mailer', 'smser'],
)

modules = ['nicos.commands.standard', 'nicos_mlz.maria.scan']

includes = ['notifiers']

devices = dict(
    Sample   = device('nicos.devices.sample.Sample',
                      description = 'The current used sample',
                     ),

    # Configure dataroot here (usually /data).
    Exp      = device('nicos_mlz.maria.devices.experiment.Experiment',
                      description = 'experiment object',
                      dataroot = '/data',
                      managerights = dict(enableDirMode=0o775,
                                          enableFileMode=0o644,
                                          disableDirMode=0o750,
                                          disableFileMode=0o440,
                                          enableOwner='jcns',
                                          enableGroup='games',
                                          disableOwner='jcns',
                                          disableGroup='maria',
                                         ),
                      mailserver = 'mailhost.frm2.tum.de',
                      mailsender = 'maria@frm2.tum.de',
                      sendmail = True,
                      zipdata = True,
                      serviceexp = 'service',
                      sample = 'Sample',
                     ),

    maria = device('nicos.devices.instrument.Instrument',
                   description = 'MAgnetic Reflectometer with Incident Angle',
                   instrument = 'MARIA',
                   responsible = 'Stefan Mattauch <s.mattauch@fz-juelich.de>',
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
                      path = None,
                      minfree = 5,
                     ),
)
