description = 'system setup'

sysconfig = dict(
    cache = 'tequila.pgaa.frm2',
    instrument = 'Instrument',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = ['commands.standard']

devices = dict(
    Sample   = device('devices.sample.Sample'),

    Instrument = device('devices.instrument.Instrument',
                        responsible = 'Dr. Petra Kudejova <petra.kudejova@frm2.tum.de>',
                       ),

    Exp      = device('devices.experiment.Experiment',
                      dataroot = '/localdata/',
                      sample = 'Sample'),

    filesink = device('devices.datasinks.AsciiDatafileSink',
                     ),

    conssink = device('devices.datasinks.ConsoleSink'),

    daemonsink = device('devices.datasinks.DaemonSink'),

    Space    = device('devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      minfree = 0.5,
                     ),
)
