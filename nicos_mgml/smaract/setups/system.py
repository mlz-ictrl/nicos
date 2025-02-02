description = 'system setup'

group = 'lowlevel'

includes = [
    'notifiers',
    'smaract',
]

sysconfig = dict(
    cache = 'localhost',
    instrument = 'smaract',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'dmnsink'],
    notifiers = ['slacker'],
)

modules = ['nicos.commands.standard']

devices = dict(
    smaract = device('nicos.devices.instrument.Instrument',
        description = 'Smaract nanomanuipulator',
        instrument = 'Smaract',
        responsible = 'P. Cermak <petr.cermak@matfyz.cuni.cz>',
        website = 'http://www.mgml.eu',
        operators = ['MGML Troja team'],
        facility = 'MGML',
    ),
    Sample = device('nicos.devices.tas.TASSample',
        description = 'sample object',
    ),
    Exp = device('nicos_mgml.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = '/data',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
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
#   Bus = device('nicos_mgml.devices.bus.Bus',
#       description = "Next departure of the bus from station 'Kuchyňka' "
#                     'to the Nádraží Holešovice',
#       fmtstr = '%s'
#   ),
)

startupcode = '''
from nicos.core import SIMULATION
if not Exp.proposal and Exp._mode != SIMULATION:
    try:
        SetMode('master')
    except Exception:
        pass
'''
