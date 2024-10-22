description = 'system setup'

group = 'lowlevel'

includes = [
            'notifiers',
           ]

sysconfig = dict(
    cache = 'localhost',
    instrument = 'master',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink'],
    notifiers = ['email', 'slacker'],
)

modules = ['nicos.commands.standard']

devices = dict(
    master = device('nicos.devices.instrument.Instrument',
        description = 'Master NICOS monitor',
        instrument = 'Master Server',
        responsible = 'P. Cermak <cermak@mag.mff.cuni.cz>',
        website = 'http://www.mgml.eu',
        operators = ['MGML Troja team'],
        facility = 'MGML',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'No sample',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/data',
        sendmail = False,
        serviceexp = 'service',
        sample = 'Sample',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
    ),
    dmnsink = device('nicos.devices.datasinks.DaemonSink',
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        warnlimits = (5., None),
        path = None,
        minfree = 5,
    ),
)