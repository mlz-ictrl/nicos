description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'demo',
    experiment = 'Exp',
    datasinks = ['conssink', 'serialsink', 'dmnsink'],
    notifiers = [],
)

modules = ['nicos.commands.standard']

devices = dict(
    demo = device('nicos.devices.instrument.Instrument',
        description = 'demo instrument',
        instrument = 'DEMO',
        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
        website = 'http://www.nicos-controls.org',
        operators = ['NICOS developer team'],
        facility = 'NICOS demo instruments',
    ),
    Sample = device('nicos.devices.tas.TASSample',
        description = 'sample object',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = 'data',
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
from nicos.core import SIMULATION
if not Exp.proposal and Exp._mode != SIMULATION:
    try:
        SetMode('master')
    except Exception:
        pass
    else:
        NewExperiment(0, 'NICOS demo experiment',
                      localcontact='Nico Suser <nico.suser@frm2.tum.de>')
        AddUser('H. Maier-Leibnitz <heinz.maier-leibnitz@frm2.tum.de')
        NewSample('Gd3CdB7')
'''
