description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'refsansctrl01.refsans.frm2',
    instrument = 'REFSANS',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'configsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard', 'refsans.commands']
includes = ['notifiers']

# SYSTEM NEVER INCLUDES OTHER SETUPS !!!


devices = dict(
    REFSANS  = device('nicos.devices.instrument.Instrument',
                      description = 'Container storing Instrument properties',
                      instrument = 'REFSANS',
                      doi = 'http://dx.doi.org/10.17815/jlsrf-1-31',
                      responsible = 'Matthias Pomm <matthias.pomm@hzg.de>',
                      # responsible = 'Dr. Jean-Francois Moulin '
                      #               '<jean-francois.moulin@hzg.de>',
                     ),

    Sample   = device('nicos.devices.sample.Sample',
                      description = 'Container storing Sample properties',
                     ),

    Exp      = device('nicos.devices.experiment.Experiment',
                      description = 'Container storing Experiment properties',
                      dataroot = '/data',
                      sample = 'Sample',
                      #~ elog = False,
                     ),

    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
                      description = 'Device saving scanfiles',
                     ),

    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
                      description = 'Device outputting logmessages to the console',
                     ),

    daemonsink = device('nicos.devices.datasinks.DaemonSink',
                        description = 'The daemon Device, coordinating all the heavy lifting',
                       ),

    configsink = device('nicos_mlz.refsans.devices.datasinks.ConfigObjDatafileSink',
                        lowlevel = True,
                       ),

    Space    = device('nicos.devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      minfree = 5,
                     ),
)
