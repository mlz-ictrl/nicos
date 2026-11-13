description = 'system setup only'
group = 'lowlevel'

sysconfig = dict(
    cache = 'hw2026.ladiff.frm2.tum.de',
    instrument = 'ladiff',
    experiment = 'Exp',
    notifiers = ['email', 'smser'],
    datasinks = ['conssink', 'filesink', 'dmnsink'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Exp = device('nicos_mlz.ladiff.devices.experiment.Experiment',
        description = 'experiment object',
        sample = 'Sample',
        dataroot = '/data',
        serviceexp = '0',
        sendmail = True,
        mailsender = 'rgeorgii@frm2.tum.de',
    ),
    Sample = device('nicos_mlz.devices.sample.Sample',
        description = 'sample object',
    ),
    ladiff = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'LaDiff',
        # doi = 'http://dx.doi.org/10.17815/jlsrf-1-21',
        responsible = 'Robert Georgii <robert.georgii@frm2.tum.de>',
        operators = ['Technische Universität München (TUM)'],
        website = 'https://mlz-garching.de/englisch/instruments/spectroscopy/ladiff.html',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    dmnsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'free space on data share',
        minfree = 10,
        path = '/data',
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free space on the log drive',
        path = '/control/log',
        visibility = (),
        warnlimits = (0.5, None),
    ),
)
