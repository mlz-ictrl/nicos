description = 'system setup for TMR'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'TMR',
    experiment = 'Exp',
    datasinks = ['conssink', 'daemonsink', 'filesink'],
    notifiers = ['email'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    TMR = device('nicos.devices.instrument.Instrument',
        description = 'Target-Moderator-Reflector in COSY\'s Big Karl '
                      'experimental area.',
        instrument = 'TMR',
        responsible = 'Ulrich Rücker <u.ruecker@fz-juelich.de>',
        facility = 'Forschungszentrum Jülich',
        operators = ['Jülich Centre for Neutron Science (JCNS)',
                     'Nuclear Physics Institute (IKP)'],
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'Currently used sample.',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'TMR experiment object.',
        dataroot = '/data',
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o664,
            disableDirMode = 0o775,
            disableFileMode = 0o664,
            owner = 'jcns',
            group = 'jcns'
        ),
        mailserver = 'mail.fz-juelich.de',
        mailsender = 'tmr@fz-juelich.de',
        sendmail = False,
        zipdata = False,
        serviceexp = 'service',
        sample = 'Sample',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        description = 'Device storing scanfiles in Ascii output format.',
        filenametemplate = ['%(session.experiment.users)s_'
                            '%(session.experiment.sample.filename)s_'
                            '%(scancounter)s.dat'],
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data.',
        path = None,
        minfree = 5,
    ),
)
