description = 'NICOS system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'TOFTOF',
    experiment = 'Exp',
    datasinks = [
        'conssink', 'filesink', 'dmnsink', 'livesink', 'tofsink'
    ],
)

modules = ['nicos.commands.standard']

devices = dict(
    TOFTOF = device('nicos.devices.instrument.Instrument',
        description = 'Virtual TOFTOF instrument',
        instrument = 'V-TofTof',
        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-40',
        website = 'http://www.mlz-garching.de/toftof',
        facility = 'NICOS demo instruments',
        operators = ['NICOS developer team'],
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The current used sample',
    ),
    Exp = device('nicos_mlz.toftof.devices.experiment.Experiment',
        description = 'The current running experiment',
        propprefix = '',
        dataroot = 'data',
        sendmail = True,
        serviceexp = 'p0',
        sample = 'Sample',
        reporttemplate = '',
        elog = True,
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o550,
            disableFileMode = 0o440,
            # owner = 'toftof',
            # group = 'toftof',
        ),
        counterfile = 'counter',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    dmnsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    livesink = device('nicos_mlz.toftof.devices.datasinks.ToftofLiveViewSink',
    ),
    tofsink = device('nicos_mlz.toftof.devices.datasinks.TofImageSink',
        filenametemplate = ['%(pointcounter)08d_0000.raw'],
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = 'data',
        minfree = 5,
    ),
)
