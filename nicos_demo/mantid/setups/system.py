description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    # notifiers = ['email', 'smser'],
)

modules = ['nicos.commands.standard']
# includes = ['notifiers', ]

devices = dict(
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = 'data',
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'The currently used sample',
    ),
    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        path = None,
        minfree = 5,
    ),
)

startupcode = '''
from nicos.core import SIMULATION
if not Exp.proposal and Exp._mode != SIMULATION:
    try:
        SetMode('master')
    except Exception:
        pass
    else:
        NewExperiment(0, 'MANTID demo experiment',
                      localcontact='Nico Suser <nico.suser@frm2.tum.de>')
        AddUser('H. Maier-Leibnitz <heinz.maier-leibnitz@frm2.tum.de')
        NewSample('Gd3CdB7')
'''
