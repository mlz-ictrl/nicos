description = 'system setup for PUMA'
group = 'lowlevel'

sysconfig = dict(
    cache = configdata('config_data.cache_host'),
    instrument = 'puma',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'nxscansink'],
    notifiers = [],
)

modules = ['nicos.commands.standard']

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
        dataroot = configdata('config_data.dataroot'),
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o700,
            disableFileMode = 0o600,
        ),
        zipdata = True,
        mailserver = 'mailhost.frm2.tum.de',
        mailsender = 'puma@frm2.tum.de',
        serviceexp = 'service',
    ),
    Sample = device('nicos.devices.tas.TASSample',
        description = 'Currently used sample',
        lattice = [4.05, 4.05, 4.05],
    ),
    nxtassink = device('nicos.nexus.NexusSink',
        templateclass = 'nicos_mlz.nexus.nexus_templates.TasTemplateProvider',
        filenametemplate = ['puma%(scancounter)07d.nxs'],
        settypes = {'scan', 'point'},  # 'subscan', },
        filemode = 0o440,
    ),
    nxscansink = device('nicos.nexus.NexusSink',
        templateclass = 'nicos_mlz.nexus.nexus_templates.ScanTemplateProvider',
        filenametemplate = ['puma%(scancounter)07d.nxs'],
        settypes = {'scan', 'point'},
        filemode = 0o440,
        device_mapping = {
            'sample': 'sample',
            'omgs': 'psi',
            'det': 'det',
            'mon': 'mon1',
            'timer': 'timer',
        },
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        filenametemplate = [
            '%(proposal)s_'
            '%(scancounter)08d.dat', '/%(year)d/cycle_%(cycle)s/'
            '%(proposal)s_'
            '%(scancounter)08d.dat'
        ],
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Free space on the log drive',
        path = configdata('config_data.logging_path'),
        visibility = (),
        warnlimits = (0.5, None),
    ),
)
