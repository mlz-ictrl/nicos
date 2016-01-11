description = 'system setup'

sysconfig = dict(
    cache = None, # 'sans1ctrl.sans1.frm2',
    instrument = 'Instrument',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = ['commands.standard']

devices = dict(
    Sample   = device('devices.sample.Sample',
                      description = 'The sample',
                     ),

    Instrument = device('devices.instrument.Instrument',
                        description = 'Facility for particle physics with cold '
                                      'neutrons',
                        doi = 'http://dx.doi.org/10.17815/jlsrf-1-48',
                        responsible = 'Dr. Jens Klenke <jens.klenke@frm2.tum.de>',
                       ),

    Exp      = device('devices.experiment.Experiment',
                      description = 'The current running experiment',
                      dataroot = '/localhome/data',
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
                      minfree = 0.5,
                     ),
)
