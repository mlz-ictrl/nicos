description = 'system setup'

sysconfig = dict(
    cache = None, # 'sans1ctrl.sans1.frm2',
    instrument = 'MEPHISTO',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email'],
)

modules = ['commands.standard']

includes = ['notifiers']

devices = dict(
    Sample   = device('devices.sample.Sample',
                      description = 'Container storing Sample properties',
                     ),

    MEPHISTO = device('devices.instrument.Instrument',
                        description = 'Facility for particle physics with cold '
                                      'neutrons',
                        doi = 'http://dx.doi.org/10.17815/jlsrf-1-48',
                        responsible = 'Dr. Jens Klenke <jens.klenke@frm2.tum.de>',
                       ),

    Exp      = device('devices.experiment.Experiment',
                      description = 'MEPHISTO Experiment ',
                      dataroot = '/localhome/data',
                      sample = 'Sample',
                     ),

    filesink = device('devices.datasinks.AsciiScanfileSink',
                      description = 'Device storing scanfiles in Ascii output format.',
                      lowlevel = True,
                     ),

    conssink = device('devices.datasinks.ConsoleScanSink',
                      description = 'Device storing console output.',
                      lowlevel = True,
                     ),

    daemonsink = device('devices.datasinks.DaemonSink',
                        description = 'Device storing deamon output.',
                        lowlevel = True,
                       ),

    Space    = device('devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      minfree = 0.5,
                     ),
)
