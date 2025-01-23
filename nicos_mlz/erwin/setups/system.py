description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'erwin',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink', 'filesink', 'livesink'],
    notifiers = ['email'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    erwin = device('nicos.devices.instrument.Instrument',
        description = 'ErwiN instrument',
        instrument = 'ErwiN',
        responsible = 'Markus Hölzel <markus.hoelzel@frm2.tum.de>',
        website = 'https://mlz-garching.de/erwin',
        operators = [
            'Technische Universität München (TUM)',
            'Karlsruhe Institute of Technology (KIT)',
        ],
    ),
    Sample = device('nicos_mlz.devices.sample.Sample',
        description = 'sample object',
    ),
    Exp = device('nicos_mlz.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = 'data',
        sample = 'Sample',
        reporttemplate = '',
        serviceexp = 'p0',
        mailsender = 'erwin@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        elog = True,
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o644,
            disableDirMode = 0o550,
            disableFileMode = 0o440,
            owner = 'erwin',
            group = 'erwin'
        ),
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos_mlz.erwin.datasinks.LiveViewSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        warnlimits = (5., None),
        path = '/data',
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
