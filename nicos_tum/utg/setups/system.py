description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'utg',
    experiment = 'Exp',
    datasinks = ['conssink', 'serialsink', 'livesink', 'dmnsink'],
    notifiers = [],
)

modules = ['nicos.commands.standard']

devices = dict(
    utg = device('nicos.devices.instrument.Instrument',
        description = 'UTG testing instrument',
        instrument = 'UTG',
        responsible = 'Martin Landesberger <martin.landesberger@utg.de>',
        website = 'https://www.utg.mw.tum.de/',
        operators = ['UTG', ],
        facility = 'TU Munich',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'sample object',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/data',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
        reporttemplate = '',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
        lowlevel = True,
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink',
        lowlevel = True,
    ),
    dmnsink = device('nicos.devices.datasinks.DaemonSink',
        lowlevel = True,
    ),
    serialsink = device('nicos.devices.datasinks.SerializedSink',
        lowlevel = True,
    ),
    livesink = device('nicos.devices.datasinks.LiveViewSink',
        lowlevel = True,
    ),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
    UBahn = device('nicos_mlz.frm2.devices.ubahn.UBahn',
        description = 'Next subway departures',
    ),
)

startupcode = '''
'''
