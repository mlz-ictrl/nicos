description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'TOPAS',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'mattermost'],
)

includes = ['notifiers']

modules = ['nicos.commands.standard']

devices = dict(
    Sample = device('nicos.devices.sample.Sample',
        description = 'Sample under investigation'
    ),

    Exp = device('nicos_mlz.devices.experiment.Experiment',
        description = 'Experiment device',
        sample = 'Sample',
        dataroot = '/data',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o700,
            disableFileMode = 0o400,
            owner = 'jcns',
            group = 'mlzinstr'
        ),
        mailsender = 'topas@frm2.tum.de',
        sendmail = True,
        zipdata = False,
    ),
    TOPAS = device('nicos.devices.instrument.Instrument',
        description = 'Time-of-flight Polarization Analysis Spectrometer',
        instrument = 'TOPAS',
        doi = '',
        responsible = 'M. Stekiel <m.stekiel@fz-juelich.de>',
        operators = [
            'Jülich Centre for Neutron Science (JCNS)',
        ],
        website = 'http://www.mlz-garching.de/topas',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        description = 'Device storing scanfiles in Ascii output format.',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        description = 'Device storing console output.',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        description = 'Device storing deamon output.',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
)
