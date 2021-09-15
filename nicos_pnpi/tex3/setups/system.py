description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    # Adapt this name to your instrument's name (also below).
    instrument = 'Instrument',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'livesink'],
    notifiers = ['email'],
)

modules = ['nicos.commands.standard', 'nicos.commands.utility']

includes = [
    'notifiers',
]

devices = dict(
    Instrument = device('nicos.devices.instrument.Instrument',
                        description = 'Texture difractometor',
                        instrument = 'TEX-3',
                        responsible = 'Dmitry Ipatov <ipatov_da@pnpi.nrcki.ru>',
                        facility = 'Petersburg Nuclear Physics Institute (PNPI)',
                        website = 'http://www.pnpi.spb.ru/'
                        ),
    Sample = device('nicos.devices.sample.Sample',
                    description = 'The current used sample',
                    ),

    email = device('nicos.devices.notifiers.Notifier'),

    Exp = device('nicos.devices.experiment.Experiment',
                 description = 'experiment object',
                 dataroot = 'data',
                 sendmail = True,
                 serviceexp = 'service',
                 sample = 'Sample',
                 ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink'),
    Space = device('nicos.devices.generic.FreeSpace',
                   description = 'The amount of free space for storing data',
                   path = None,
                   warnlimits = (5., None),
                   minfree = 5,
                   ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
                      description = 'Space on log drive',
                      path = 'log',
                      warnlimits = (.5, None),
                      minfree = 0.5,
                      lowlevel = True,
                      ),
)

# startupcode = '''

# SetDetectors(det)

# '''
