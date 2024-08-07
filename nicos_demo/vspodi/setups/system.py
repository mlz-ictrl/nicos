description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = configdata('config_data.host'),
    instrument = 'Spodi',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'spodilivesink',
        'spodisink',
    ],
    # notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']

# includes = ['notifiers']

devices = dict(
    Spodi = device('nicos.devices.instrument.Instrument',
        description = 'Virtual SPODI instrument',
        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
        instrument = 'V-SPODI',
        website = 'http://www.mlz-garching.de/spodi',
        operators = ['NICOS developer team'],
        facility = 'NICOS demo instruments',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-24',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = configdata('config_data.dataroot'),
        sendmail = True,
        serviceexp = 'p0',
        sample = 'Sample',
        elog = True,
        managerights = dict(
            enableDirMode = 0o775,
            enableFileMode = 0o644,
            disableDirMode = 0o550,
            disableFileMode = 0o440,
            # owner = 'spodi',
            # group = 'spodi'
        ),
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    spodisink = device('nicos_mlz.spodi.datasinks.CaressHistogram',
        filenametemplate = ['m1%(pointcounter)08d.ctxt'],
        detectors = ['adet'],
    ),
    spodilivesink = device('nicos_mlz.spodi.datasinks.LiveViewSink',
        correctionfile='nicos_mlz/spodi/data/detcorrection.dat'
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = configdata('config_data.dataroot'),
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = configdata('config_data.logging_path'),
        minfree = 0.5,
        visibility = (),
    ),
)
