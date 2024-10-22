description = 'system setup'

group = 'lowlevel'

includes = [
            'notifiers',
           ]

sysconfig = dict(
    cache = 'kfes64.troja.mff.cuni.cz:14869',
    instrument = 'magnet20t',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'dmnsink'],
    notifiers = ['email', 'slacker'],
)

modules = ['nicos.commands.standard']

devices = dict(
    magnet20t = device('nicos.devices.instrument.Instrument',
        description = 'Cryoenics magnet with vertical field up to 20T',
        instrument = '20T magnet',
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
        templates = 'templates',
        sendmail = True,
        mailserver = 'smtp.karlov.mff.cuni.cz:465',
        mailsender = 'noreply@mgml.eu',
        mailsecurity = 'ssl',
        mailuser = '0mgml-panel',
        serviceexp = 'service',
        sample = 'Sample',
        cryostat = 'Cryostat'
    ),
    filesink = device('nicos_mgml.devices.datasinks.AsciiScanfileSink',
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
#        description = "Next departure of the bus from station 'Kuchyňka' "
#                      'to the Nádraží Holešovice',
#        fmtstr = '%s'
#    ),
)

startupcode = '''
from nicos.core import SIMULATION
if not Exp.proposal and Exp._mode != SIMULATION:
    try:
        SetMode('master')
    except Exception:
        pass
'''
