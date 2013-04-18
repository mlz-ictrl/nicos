description = 'system setup'
group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'liveplot'],
    notifiers = [],
)

modules = ['nicos.commands.standard', 'nicos.commands.taco']

devices = dict(
    Sample   = device('devices.tas.TASSample'),

    Exp      = device('devices.experiment.Experiment',
                      dataroot = 'data',
                      sendmail = True,
                      managerights = False,
                      serviceexp = '0',
                      sample = 'Sample'
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
if not Exp.proposal:
    SetMode('master')
    NewExperiment(0)
'''
