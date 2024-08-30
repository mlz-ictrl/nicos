description = 'system setup'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'POLI',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'livesink'],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard', 'nicos_mlz.poli.commands']

includes = ['notifiers', 'table_lifting', 'table', 'mono', 'slits']

devices = dict(
    POLI = device('nicos.devices.sxtal.instrument.LiftingSXTal',
        description = 'Virtual McStas-backed POLI instrument',
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
        sample = 'Sample',
        dataroot = 'data',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o700,
            disableFileMode = 0o600,
        ),
        sendmail = True,
        zipdata = True,
        mailserver = 'mailhost.frm2.tum.de',
        mailsender = 'vpoli@frm2.tum.de',
        serviceexp = 'p0',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = 'data',
        minfree = 5,
    ),
)

extended = dict(
    poller_cache_reader = ['liftingctr']
)
