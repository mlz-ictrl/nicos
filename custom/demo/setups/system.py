description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'tas',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'serialsink'],
    notifiers = [],
)

modules = ['commands.standard'] # , 'jcns.commands']

devices = dict(
    tas        = device('devices.instrument.Instrument',
                        description = 'demo instrument',
                        instrument = 'DEMO',
                        responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>',
                       ),

    Sample     = device('devices.tas.TASSample',
                        description = 'sample object',
                       ),

    Exp        = device('devices.experiment.Experiment',
                        description = 'experiment object',
                        dataroot = 'data',
                        sendmail = True,
                        serviceexp = 'service',
                        sample = 'Sample',
                        reporttemplate = '',
                       ),

    filesink   = device('devices.datasinks.AsciiDatafileSink',
                        lowlevel = True,
                       ),

    conssink   = device('devices.datasinks.ConsoleSink',
                        lowlevel = True,
                       ),

    daemonsink = device('devices.datasinks.DaemonSink',
                        lowlevel = True,
                       ),

    serialsink = device('devices.datasinks.SerializedSink',
                        lowlevel = True,
                       ),

    Space     = device('devices.generic.FreeSpace',
                       description = 'The amount of free space for storing data',
                       path = None,
                       minfree = 5,
                      ),

    UBahn     = device('frm2.ubahn.UBahn',
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
        NewExperiment(0, 'NICOS demo experiment', localcontact='N. N. <noreply@frm2.tum.de>')
        AddUser('H. Maier-Leibnitz')
        NewSample('Gd3CdB7')
'''
