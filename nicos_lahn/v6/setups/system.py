description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    # Adapt this name to your instrument's name (also below).
    instrument = 'V6',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'livesink'],
    #notifiers = ['email'],
)

modules = ['nicos.commands.standard']

includes = [
#    'notifiers',
]

devices = dict(
    V6 = device('nicos.devices.instrument.Instrument',
        description = 'Neutron Reflectometer (Polarized)',
        instrument = 'V6',
        responsible = 'Marina Tortarolo <tortarol@tandar.cnea.gov.ar>',
        website = 'https://www.lahn.cnea.gov.ar',
        operators = ['Laboratorio Argentino de Haces de Neutrones'],
        facility = 'LAHN',
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
        visibility = ('devlist',),
    ),
)
