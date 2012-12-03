description = 'system setup'

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'liveplot'],
    notifiers = [],
)

modules = ['nicos.commands.taco']

devices = dict(
    Sample   = device('devices.tas.TASSample'),

    Exp      = device('devices.experiment.Experiment',
                      dataroot = 'data',
                      sample = 'Sample',
                     ),

    filesink = device('devices.datasinks.AsciiDatafileSink'),

    conssink = device('devices.datasinks.ConsoleSink'),

    daemonsink = device('devices.datasinks.DaemonSink'),

    liveplot = device('devices.datasinks.GraceSink'),

    Space    = device('devices.generic.FreeSpace',
                      path = None,
                      minfree = 5,
                     ),
)
