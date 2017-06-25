description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'refsansctrl01.refsans.frm2',
    instrument = 'REFSANS',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'configsink'],
    notifiers = ['email', 'smser'],
)

modules = ['commands.standard', 'refsans.commands']
includes = ['notifiers']

# SYSTEM NEVER INCLUDES OTHER SETUPS !!!


devices = dict(
    REFSANS  = device('devices.instrument.Instrument',
                      description = 'Container storing Instrument properties',
                      instrument = 'REFSANS',
                      doi = 'http://dx.doi.org/10.17815/jlsrf-1-31',
                      responsible = 'Matthias Pomm <matthias.pomm@hzg.de>',
                      # responsible = 'Dr. Jean-Francois Moulin '
                      #               '<jean-francois.moulin@hzg.de>',
                     ),

    Sample   = device('devices.sample.Sample',
                      description = 'Container storing Sample properties',
                     ),

    Exp      = device('devices.experiment.Experiment',
                      description = 'Container storing Experiment properties',
                      dataroot = '/data',
                      sample = 'Sample',
                      #~ elog = False,
                     ),

    filesink = device('devices.datasinks.AsciiScanfileSink',
                      description = 'Device saving scanfiles',
                     ),

    conssink = device('devices.datasinks.ConsoleScanSink',
                      description = 'Device outputting logmessages to the console',
                     ),

    daemonsink = device('devices.datasinks.DaemonSink',
                        description = 'The daemon Device, coordinating all the heavy lifting',
                       ),

    configsink = device('refsans.datasinks.ConfigObjDatafileSink',
                        lowlevel = True,
                       ),

    Space    = device('devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      minfree = 5,
                     ),
)
