description = 'system setup'
group = 'lowlevel'

sysconfig = dict(
    cache = 'nectarhw.nectar.frm2.tum.de',
    instrument = 'Instrument',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = [
    'nicos.commands.standard',
    'nicos_mlz.antares.commands',
    'nicos_mlz.nectar.commands',
]

includes = ['notifiers']

devices = dict(
    Sample = device('nicos_mlz.devices.sample.Sample',
        description = 'sample object',
    ),
    Exp = device('nicos_mlz.antares.devices.Experiment',
        description = 'experiment object',
        dataroot = '/data/FRM-II',
        sample = 'Sample',
        mailsender = 'nectar@frm2.tum.de',
        zipdata = False,
        managerights = {},
    ),
    Instrument = device('nicos.devices.instrument.Instrument',
        description = 'NECTAR instrument',
        instrument = 'NECTAR',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-45',
        responsible = 'Adrian Losko <adrian.losko@frm2.tum.de>',
        operators = ['Technische Universität München (TUM)'],
        website = 'http://www.mlz-garching.de/nectar',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'Free Space in the RootDir of nectarhw',
        path = '/',
        minfree = 5,
    ),
    HomeSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free Space in the home directory of user nectar',
        path = '/localhome/nectar',
        minfree = 1,
    ),
    DataSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free Space on the DataStorage',
        minfree = 50,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free space on the log drive',
        path = '/control/log',
        visibility = (),
        warnlimits = (0.5, None),
    ),
)
