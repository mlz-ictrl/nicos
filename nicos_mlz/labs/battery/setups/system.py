description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'battery',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink'],
    notifiers = [],
)

modules = ['nicos.commands.standard']

devices = dict(
    battery = device('nicos.devices.instrument.Instrument',
        description = 'battery test stand',
        instrument = 'Battery test lab',
        responsible = 'A. Senyshyn <Anatoliy.Senyshyn@frm2.tum.de>',
        website = 'http://www.nicos-controls.org',
        operators = ['MLZ'],
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'sample object',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/home/localadmin/data',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        warnlimits = (5., None),
        path = None,
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = 'log',
        warnlimits = (.5, None),
        minfree = 0.5,
        lowlevel = True,
    ),
)

startupcode = '''
'''
