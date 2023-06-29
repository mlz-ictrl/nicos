description = 'system setup'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

sysconfig = dict(
    cache = 'localhost',
    instrument = 'XReSD',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'livesink'],
    notifiers = [],  # ['email'],
)

modules = ['nicos.commands.standard']

includes = [
    'notifiers',
]

devices = dict(
    XReSD = device('nicos.devices.instrument.Instrument',
        description = 'X-ray Residual Stress Diffractometer',
        instrument = 'XReSD',
        responsible = 'Bastian Veltel <bastian.veltel@frm2.tum.de>',
        website = 'https://mlz-garching.de/physics-lab',
        operators = ['MLZ'],
        facility = 'mlz',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/data/04_RSXRD',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos_mlz.labs.physlab.xresd.datasinks.LiveViewSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = '/data/04_RSXRD',
        warnlimits = (5., None),
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = '/control/log',
        warnlimits = (.5, None),
        minfree = 0.5,
        visibility = (),
    ),
)
