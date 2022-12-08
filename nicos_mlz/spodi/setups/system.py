description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'spodictrl.spodi.frm2.tum.de',
    instrument = 'Spodi',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'spodilivesink',
        'spodisink', 'nxsink',
    ],
    notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard', 'nicos.commands.utility']

includes = ['notifiers']

devices = dict(
    Spodi = device('nicos.devices.instrument.Instrument',
        description = 'instrument object',
        instrument = 'SPODI',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-24',
        responsible = 'Markus Hoelzel <markus.hoelzel@frm2.tum.de>',
        website = 'http://www.mlz-garching.de/spodi',
        operators = [
            'Technische Universität München (TUM)',
            'Karlsruher Institut für Technologie (KIT)',
        ],
    ),
    Sample = device('nicos_mlz.devices.sample.Sample',
        description = 'The currently used sample',
    ),

    Exp = device('nicos_mlz.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/data',
        serviceexp = 'p0',
        sample = 'Sample',
        mailsender = 'spodi@frm2.tum.de',
        mailserver = 'mailhost.frm2.tum.de',
        elog = True,
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o644,
            disableDirMode = 0o550,
            disableFileMode = 0o440,
            owner = 'spodi',
            group = 'spodi'
        ),
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    spodilivesink = device('nicos_mlz.spodi.datasinks.LiveViewSink',
        correctionfile='nicos_mlz/spodi/data/detcorrection.dat'
    ),
    spodisink = device('nicos_mlz.spodi.datasinks.CaressHistogram',
        description = 'SPODI specific histogram file format',
        filenametemplate = ['run%(pointcounter)06d.ctxt'],
        detectors = ['adet'],
    ),
    nxsink = device('nicos.nexus.NexusSink',
        templateclass='nicos_mlz.nexus.SpodiTemplateProvider',
        settypes = {'point',},
        filenametemplate = ['m1%(pointcounter)08d.nxs'],
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = '/control/log',
        minfree = 0.5,
        visibility = (),
    ),
)

display_order = 70
