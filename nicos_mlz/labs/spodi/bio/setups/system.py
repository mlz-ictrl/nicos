description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'bio',
    experiment = 'Exp',
    datasinks = [
        'conssink', 'filesink', 'daemonsink', 'livesink',  # 'rawsink',
    ],
    notifiers = [],
)

modules = [
    'nicos.commands.standard',
    'nicos_mlz.labs.spodi.bio.commands',
]

includes = [
    'notifiers',
]

devices = dict(
    bio = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'BIO',
        responsible = 'Anatoliy Senyshyn <anatoliy.senyshyn@frm2.tum.de>',
        website = 'http://www.mlz-garching.de/spodi',
        operators = ['MLZ'],
        facility = 'MLZ',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = 'data',
        sendmail = True,
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink'),
    rawsink = device ('nicos.devices.datasinks.RawImageSink',
        description = 'Saves image data in RAW format',
        filenametemplate = [
            '%(proposal)s_%(pointcounter)s.raw',
            # '%(proposal)s_%(scancounter)s_%(pointcounter)s_%(pointnumber)s.raw'
        ],
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = 'data',
        warnlimits = (5., None),
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = '/control/log',
        warnlimits = (.5, None),
        minfree = 0.5,
        visibility = (),
    ),
)
