description = 'NICOS system setup'

sysconfig = dict(
    cache = 'sehw.se.frm2',
    instrument = 'SE',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'dmnsink'],
    notifiers = ['emailer', 'smser'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    SE       = device('nicos.devices.instrument.Instrument',
                      description = 'instrument object',
                      responsible = 'juergen.peters@frm2.tum.de',
                      instrument = 'SE',
                     ),

    Sample   = device('nicos.devices.sample.Sample',
                      description = 'sample object',
                     ),

    Exp      = device('nicos.devices.experiment.Experiment',
                      description = 'experiment object',
                      dataroot = '/data',
                      sample = 'Sample',
                      elog = False,
                     ),

    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
                      lowlevel = True,
                     ),

    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
                      lowlevel = True,
                     ),

    dmnsink  = device('nicos.devices.datasinks.DaemonSink',
                      lowlevel = True,
                     ),

    Space    = device('nicos.devices.generic.FreeSpace',
                      description = 'The free space on the data storage',
                      path = '/data',
                      minfree = 5,
                     ),
)
