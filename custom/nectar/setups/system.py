description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'nectarhw.nectar.frm2',
    instrument = 'Instrument',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['commands.basic', 'commands.standard',
           'antares.commands', 'nectar.commands', ]

includes = ['notifiers', ]

devices = dict(
    Sample   = device('devices.sample.Sample',
                      description = 'sample object',
                     ),

    Exp      = device('antares.experiment.Experiment',
                      description = 'experiment object',
                      dataroot = '/data/FRM-II',
                      propdb = '/etc/propdb',
                      serviceexp = 'service',
                      sample = 'Sample',
                      mailsender = 'nectar@frm2.tum.de',
                      sendmail = False,
                      zipdata = False,
                      managerights = {},
                     ),

    Instrument = device('devices.instrument.Instrument',
                        description = 'NECTAR instrument',
                        instrument = 'NECTAR',
                        doi = 'http://dx.doi.org/10.17815/jlsrf-1-45',
                        responsible = 'Christoph Genreith <christoph.genreith@frm2.tum.de>',
                       ),

    filesink = device('devices.datasinks.AsciiScanfileSink',
                      lowlevel = True,
                     ),

    conssink = device('devices.datasinks.ConsoleScanSink',
                      lowlevel = True,
                     ),

    daemonsink = device('devices.datasinks.DaemonSink',
                        lowlevel = True,
                       ),

    Space    = device('devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      path = None,
                      minfree = 5,
                     ),
)
