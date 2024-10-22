description = 'system setup'

group = 'lowlevel'

includes = [
            'notifiers',
           ]

sysconfig = dict(
    cache = 'localhost',
    instrument = 'cart',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'dmnsink'],
    notifiers = ['email', 'slacker'],
)

modules = ['nicos.commands.standard']

devices = dict(
    cart = device('nicos.devices.instrument.Instrument',
        description = 'Universal cart communicating with PPMS',
        instrument = 'universal cart',
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
        path = '/data',
        minfree = 5,
    ),
#    Bus = device('nicos_mgml.devices.bus.Bus',
#        description = "Next departure of the bus from station 'Kuchynka' "
#                      'to the Nádrazi Holesovice',
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
