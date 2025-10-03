description = 'system setup'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'POLI',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard', 'nicos_mlz.poli.commands',
           'nicos_mlz.poli.he_cell_commands']

includes = ['notifiers', 'table', 'mono', 'slits', 'reactor', 'shutter']

devices = dict(
    POLI = device('nicos.devices.sxtal.instrument.LiftingSXTal',
        description = 'The POLI instrument',
        responsible = 'J. Xu <jianhui.xu@frm2.tum.de>',
        instrument = 'POLI',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-22',
        mono = 'wavelength',
        gamma = 'gamma',
        omega = 'sth',
        nu = 'liftingctr',
        operators = ['RWTH Aachen University'],
        website = 'http://www.mlz-garching.de/poli',
    ),
    Sample = device('nicos.devices.sxtal.sample.SXTalSample',
        description = 'The currently used sample',
    ),

    Exp = device('nicos_mlz.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/data',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o700,
            disableFileMode = 0o400,
            owner = 'jcns',
            group = 'mlzinstr'
        ),
        sendmail = True,
        mailsender = 'poli@frm2.tum.de',
        serviceexp = 'p0',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        minfree = 5,
    ),
)

extended = dict(
    poller_cache_reader = ['liftingctr']
)
