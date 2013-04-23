description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'demo',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'liveplot'],
    notifiers = [],
)

modules = ['nicos.commands.standard'] # , 'jcns.commands']

devices = dict(
    demo     = device('devices.instrument.Instrument',
                      instrument = 'DEMO',
                      responsible = 'R. Esponsible <r.esponsible@frm2.tum.de>'),

    Sample   = device('devices.tas.TASSample'),

    Exp      = device('devices.experiment.Experiment',
                      dataroot = 'data',
                      sendmail = True,
                      managerights = False,
                      serviceexp = '0',
                      sample = 'Sample',
                     ),

    filesink = device('devices.datasinks.AsciiDatafileSink'),

    conssink = device('devices.datasinks.ConsoleSink'),

    daemonsink = device('devices.datasinks.DaemonSink'),

    liveplot = device('devices.datasinks.GraceSink'),

    Space    = device('devices.generic.FreeSpace',
                      path = None,
                      minfree = 5,
                     ),

    UBahn    = device('frm2.ubahn.UBahn'),
)

startupcode = '''
try:
    if not Exp.proposal:
        SetMode('master')
        NewExperiment(0, 'NICOS demo experiment', localcontact='N. N.')
        AddUser('H. Maier-Leibnitz')
        NewSample('Gd3CdB7')
except Exception:
    pass
'''
