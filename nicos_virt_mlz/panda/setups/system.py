description = 'system setup for PANDA'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email'],
    instrument = 'panda',
    experiment = 'Exp',
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Exp = device('nicos_mlz.panda.devices.experiment.PandaExperiment',
        description = 'Experiment device for Panda',
        sample = 'Sample',
        dataroot = 'data',
        templates = 'templates',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o700,
            disableFileMode = 0o600,
        ),
        sendmail = True,
        zipdata = True,
        mailserver = 'mailhost.frm2.tum.de',
        mailsender = 'vpanda@frm2.tum.de',
    ),
    panda = device('nicos.devices.instrument.Instrument',
        description = 'Virtual McStas-backed PANDA spectrometer',
        instrument = 'VPANDA',
        responsible = 'Astrid Schneidewind <a.schneidewind@fz-juelich.de>',
        operators = ['Jülich Centre for Neutron Science (JCNS)'],
        website = 'https://mlz-garching.de/panda',
    ),
    Sample = device('nicos.devices.tas.TASSample',
        description = 'Sample under investigation',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        description = 'metadevice storing the scanfiles',
        filenametemplate = ['%(proposal)s_%(scancounter)08d.dat'],
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        description = 'device used for console-output',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        description = 'device used for output from the daemon',
    ),
)
