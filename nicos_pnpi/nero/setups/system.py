description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'Instrument',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'livesink', 'nxsink'],
    notifiers = ['email'],
)

modules = ['nicos.commands.standard']

includes = [
    'notifiers',
]

devices = dict(
    Instrument = device('nicos.devices.instrument.Instrument',
        description = 'reflectometer',
        instrument = 'NERO',
        responsible = 'Matveev Vasiliy <matveev_va@pnpi.nrcki.ru>',
        facility = 'PNPI',
        website = 'http://www.pnpi.spb.ru/en/facilities/reactor-pik',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The current used sample',
    ),

    email = device('nicos.devices.notifiers.Notifier'),

    Exp = device('nicos.devices.experiment.Experiment',
        description = 'my experiment',
        dataroot = 'data',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
    ),

    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink'),

    nxsink = device('nicos.nexus.nexussink.NexusSink',
                    templateclass = 'nicos_pnpi.nero.templates.'\
                                    'nxtemplate.NxTemplateCount',
                    filenametemplate = ['NERO%(scancounter)08d.hdf5'],
                    subdir = 'nxdata',
                    detectors = ['det'],
                    settypes = set(['point','scan']),
                    ),

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
