# A detailed description of the setup file structure and it's elements is
# available here: https://forge.frm2.tum.de/nicos/doc/nicos-stable/setups/
#
# Please remove these lines after copying this file.

description = 'system setup'

group = 'lowlevel'

instrument_values = configdata('instrument.values')

sysconfig = dict(
    cache = 'localhost',
    # Adapt this name to your instrument's name (also below).
    instrument = 'XReSD',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'livesink'],
    notifiers = [],  # ['email'],
)

modules = ['nicos.commands.standard']

includes = [
    'notifiers',
    'incident',
    'shutter',
    'dectris',
    'sample',
    'd8',
    'hv',
]

devices = dict(
    XReSD = device('nicos.devices.instrument.Instrument',
        description = 'X-ray Residual Stress Diffractometer',
        instrument = 'XReSD',
        responsible = 'A. Book <alexander.book@frm2.tum.de>',
        website = 'https://mlz-garching.de/physics-lab',
        operators = ['MLZ'],
        facility = 'mlz',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),

    # Configure dataroot here (usually /data).
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = 'data',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        warnlimits = (5., None),
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = 'log',
        warnlimits = (.5, None),
        minfree = 0.5,
        visibility = (),
    ),
)
