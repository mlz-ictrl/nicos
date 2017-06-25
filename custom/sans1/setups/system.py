description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'sans1ctrl.sans1.frm2',
    instrument = 'Instrument',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email'],
)

modules = ['commands.standard', 'sans1.commands']

includes = ['notifiers']

devices = dict(
    Sample   = device('sans1.sans1_sample.Sans1Sample',
                      description = 'sample',
                     ),

    Instrument = device('devices.instrument.Instrument',
                        description = 'SANS1 instrument',
                        instrument = 'SANS-1',
                        doi = 'http://dx.doi.org/10.17815/jlsrf-1-32',
                        responsible = 'Dr. Andre Heinemann <Andre.Heinemann@hzg.de>',
                       ),

    Exp      = device('frm2.experiment.Experiment',
                      description = 'experiment',
                      dataroot = '/data/nicos',
                      propdb = '/sans1control/propdb',
                      sample = 'Sample',
                      sendmail = True,
                      mailsender = 'sans1@frm2.tum.de',
                     ),

    filesink = device('devices.datasinks.AsciiScanfileSink',
                      description = 'filesink',
                     ),

    conssink = device('devices.datasinks.ConsoleScanSink',
                      description = 'conssink',
                     ),

    daemonsink = device('devices.datasinks.DaemonSink',
                        description = 'daemonsink',
                       ),

    Space    = device('devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      # only specify if differing from Exp.dataroot
                      #path = '/data/nicos',
                      minfree = 0.5,
                     ),
)
