description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'demo',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'serialsink', 'liveplot'],
    notifiers = [],
)

modules = ['nicos.commands.standard'] # , 'jcns.commands']

devices = dict(
    demo     = device('devices.instrument.Instrument',
                      instrument = 'DEMO',
                      responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>,'
                                    'A. Demo <a.demo@frm2.tum.de>',
                     ),

    Sample   = device('devices.tas.TASSample'),

    Exp      = device('devices.experiment.Experiment',
                      dataroot = 'data',
                      sendmail = True,
                      serviceexp = 'service',
                      sample = 'Sample',
                      localcontact = 'R. Esponsible ' \
                                    '<r.esponsible@frm2.tum.de>',
                      reporttemplate = '',
                     ),

    filesink = device('devices.datasinks.AsciiDatafileSink'),

    conssink = device('devices.datasinks.ConsoleSink'),

    daemonsink = device('devices.datasinks.DaemonSink'),

    liveplot = device('devices.datasinks.GraceSink'),

    serialsink = device('devices.datasinks.SerializedSink'),

    Space    = device('devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      path = None,
                      minfree = 5,
                     ),

    UBahn    = device('frm2.ubahn.UBahn'),
)

startupcode = '''
from nicos.core import SIMULATION
if not Exp.proposal and Exp._mode != SIMULATION:
    try:
        SetMode('master')
    except Exception:
        pass
    else:
        NewExperiment(0, 'NICOS demo experiment', localcontact='N. N.')
        AddUser('H. Maier-Leibnitz')
        NewSample('Gd3CdB7')
'''
