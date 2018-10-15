description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
#    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

#includes = ['notifiers']

devices = dict(
    V20 = device('nicos.devices.instrument.Instrument',
                      description = 'instrument object',
                      instrument = 'V20',
                      responsible = 'Robin Woracek <robin.woracek@esss.se>',
                      facility='Helmholtz Zentrum Berlin',
                      website='https://www.helmholtz-berlin.de/pubbin/igama_output?' \
                              'modus=einzel&sprache=de&gid=1845&typoid=50726'
                     ),

    Sample   = device('nicos.devices.sample.Sample',
                      description = 'The current used sample',
                     ),

    Exp      = device('nicos.devices.experiment.Experiment',
                      description = 'experiment object',
                      dataroot = '/opt/nicos-data/data',
                      sendmail = True,
                      serviceexp = 'p0',
                      sample = 'Sample',
                     ),

    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
                     ),

    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
                     ),

    daemonsink = device('nicos.devices.datasinks.DaemonSink',
                       ),

    Space    = device('nicos.devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      path = '/opt/nicos-data/data',
                      minfree = 5,
                     ),
)
