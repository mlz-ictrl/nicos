description = 'system setup for PUMA'
group = 'lowlevel'

sysconfig = dict(
    cache = 'pumahw.puma.frm2.tum.de',
    instrument = 'puma',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'nxsink'],
    notifiers = ['email'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    puma = device('nicos.devices.instrument.Instrument',
        description = 'DAS PUMA',
        instrument = 'PUMA',
        responsible = 'J. T. Park <jitae.park@frm2.tum.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-36',
        website = 'http://www.mlz-garching.de/puma',
        operators = [
            'Technische Universität München (TUM)',
            'Institut für Physikalische Chemie, Georg-August-Universität '
            'Göttingen',
        ],
    ),
    Exp = device('nicos_mlz.panda.devices.experiment.PandaExperiment',
        description = 'Experiment of PUMA',
        sample = 'Sample',
        dataroot = '/data',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o700,
            disableFileMode = 0o600,
            owner = 'nicd',
            group = 'puma'
        ),
        sendmail = True,
        zipdata = True,
        mailserver = 'mailhost.frm2.tum.de',
        mailsender = 'puma@frm2.tum.de',
    ),
    Sample = device('nicos_mlz.devices.sample.TASSample',
        description = 'Currently used sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        description = 'metadevice storing the scanfiles',
        filenametemplate = [
            '%(proposal)s_%(scancounter)08d.dat',
            '/%(year)d/cycle_%(cycle)s/%(proposal)s_%(scancounter)08d.dat'
        ],
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        description = 'handles console output',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
        description = 'handles I/O inside daemon',
    ),
    nxsink = device('nicos.nexus.NexusSink',
        templateclass = 'nicos_mlz.puma.nexus.templates.PumaTemplateProvider',
        filenametemplate = ['%(scancounter)07d.nxs'],
        settypes = {'scan', 'point'},  # 'subscan', },
        device_mapping = {
            'ss1': 'slit1',
            'ss2': 'slit2',
            'ms': 'vs',
        },
        filemode = 0o440,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free space on the log drive',
        path = '/control/log',
        visibility = (),
        warnlimits = (0.5, None),
    ),
)
