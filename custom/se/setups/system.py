description = 'NICOS system setup'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'SE',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'dmnsink'],
    notifiers = ['emailer', 'smser'],
)

modules = ['commands.standard']

includes = ['notifiers']

devices = dict(
    SE       = device('devices.instrument.Instrument',
                      description = 'instrument object',
                      responsible = 'juergen.peters@frm2.tum.de',
                      instrument = 'SE',
                     ),

    Sample   = device('devices.sample.Sample',
                      description = 'sample object',
                     ),

    Exp      = device('devices.experiment.Experiment',
                      description = 'experiment object',
                      dataroot = '/data',
                      sample = 'Sample',
                      elog = False,
                     ),

    filesink = device('devices.datasinks.AsciiScanfileSink',
                      lowlevel = True,
                     ),

    conssink = device('devices.datasinks.ConsoleScanSink',
                      lowlevel = True,
                     ),

    dmnsink  = device('devices.datasinks.DaemonSink',
                      lowlevel = True,
                     ),

    Space    = device('devices.generic.FreeSpace',
                      description = 'The free space on the data storage',
                      path = '/data',
                      minfree = 5,
                     ),
)
