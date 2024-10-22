description = 'system setup'

group = 'lowlevel'

includes = [
    'notifiers',
]

sysconfig = dict(
    cache = 'localhost',
    instrument = 'dr9',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'dmnsink'],
    notifiers = ['email', 'slacker'],
)

modules = ['nicos.commands.standard']

devices = dict(
    dr9 = device('nicos.devices.instrument.Instrument',
        description = 'Cryomagnetics magnet with vertical field up to 9T',
        instrument = '9T magnet',
        responsible = 'P. Cermak <cermak@mag.mff.cuni.cz>',
        website = 'http://www.mgml.eu',
        operators = ['MGML Troja team'],
        facility = 'MGML',
    ),
    Sample = device('nicos.devices.tas.TASSample',
        description = 'sample object',
    ),
    Cryostat = device('nicos.devices.generic.DeviceAlias'),
    Exp = device('nicos_mgml.devices.experiment.HeliumExperiment',
        description = 'experiment object',
        dataroot = '/data',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
        cryostat = 'Cryostat'
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink',
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
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = 'log',
        warnlimits = (.5, None),
        minfree = 0.5,
        visibility = (),
    ),
#    Bus = device('nicos_mgml.devices.bus.Bus',
#        description = "Next departure of the bus from station 'Kuchynka' "
#                      'to the Nádrazi Holesovice',
#        fmtstr = '%s'
#    ),
)

startupcode = '''
'''
