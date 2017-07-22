description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'emc',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    emc      = device('nicos.devices.instrument.Instrument',
                      description = 'ElectroMagnetic Compatibility',
                      instrument = 'EMC',
                      responsible = 'F. Beule <f.beule@fz-juelich.de>',
                     ),

    Sample   = device('nicos.devices.sample.Sample',
                      description = 'The current used sample',
                     ),

    # Configure dataroot here (usually /data).
    Exp      = device('nicos.devices.experiment.Experiment',
                      description = 'experiment object',
                      dataroot = 'data',
                      sendmail = True,
                      serviceexp = 'service',
                      sample = 'Sample',
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
