description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = configdata('config_data.cache_host'),
    instrument = 'ANTARES',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'livesink',],
    notifiers = [],
)

modules = [
    'nicos.commands.standard',
    'nicos_mlz.antares.commands'
]

devices = dict(
    Sample = device('nicos.devices.experiment.Sample',
        description = 'Default Sample',
    ),
    Exp = device('nicos_mlz.antares.devices.Experiment',
        description = 'Antares Experiment',
        dataroot = configdata('config_data.dataroot'),
        sample = 'Sample',
        propprefix = 'p',
        templates = 'templates',
        zipdata = False,
        managerights = dict(
            enableDirMode = 0o770,
            enableFileMode = 0o660,
            disableDirMode = 0o550,
            disableFileMode = 0o440,
        ),
    ),
    ANTARES = device('nicos.devices.instrument.Instrument',
        description = 'Antares Instrument',
        instrument = 'ANTARES',
        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-42',
        operators = ['NICOS developer team'],
        website = 'http://www.mlz-garching.de/antares',
        facility = 'NICOS demo instruments',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        filemode=0o440,
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink'),
    DataSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free Space on the DataStorage',
        path = configdata('config_data.dataroot'),
        minfree = 100,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free space on the log drive',
        path = configdata('config_data.logging_path'),
        visibility = (),
        warnlimits = (0.5, None),
    ),
)
