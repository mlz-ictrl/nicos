description = 'system setup'
group = 'lowlevel'
includes = [
    'notifiers',
]

sysconfig = dict(
    cache = 'localhost',
    instrument = 'reseda',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'livesink',],
    notifiers = [], # ['email'],
)

modules = ['nicos.commands.standard', 'nicos_mlz.reseda.tuning_commands', 'nicos_mlz.reseda.commands']

devices = dict(
    Sample = device('nicos_mlz.devices.sample.Sample',
        description = 'The sample',
    ),
    reseda = device('nicos.devices.instrument.Instrument',
        description = 'Resonance spin echo spectrometer',
        instrument = 'RESEDA',
        responsible = 'Johanna Jochum <johanna.jochum@frm2.tum.de>',
        doi = 'http://dx.doi.org/10.17815/jlsrf-1-37',
        website = 'http://www.mlz-garching.de/reseda',
        operators = ['Technische Universität München (TUM)'],
    ),
    Exp = device('nicos_mlz.reseda.devices.Experiment',
        description = 'Experiment object',
        dataroot = '/localdata',
        sendmail = True,
        serviceexp = 'p0',
        sample = 'Sample',
        mailsender = 'reseda@frm2.tum.de',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    daemonsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
    ),
    DataSpace = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = '/localdata',
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = '/control/log',
        minfree = 1.5,
        visibility = (),
    ),
    LiveImgSink = device('nicos.devices.datasinks.PNGLiveFileSink',
        description = 'Saves live image as .png every now and then',
        filename = '/control/webroot/live.png',
        interval = 1,
    ),
)
