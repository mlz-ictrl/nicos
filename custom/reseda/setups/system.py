description = 'system setup'

sysconfig = dict(
    cache = 'resedahw',
    instrument = None,
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

modules = ['nicos.commands.standard', 'nicos.commands.taco']

devices = dict(
    Sample   = device('devices.tas.TASSample'),

    Exp      = device('frm2.experiment.Experiment',
                      dataroot = '/data',
                      sendmail = True,
                      serviceexp = '0',
                      sample = 'Sample',
                      mailsender = 'reseda@frm2.tum.de',
                      propdb = '/etc/proposaldb',
                     ),

    filesink = device('devices.datasinks.AsciiDatafileSink'),

    conssink = device('devices.datasinks.ConsoleSink'),

    daemonsink = device('devices.datasinks.DaemonSink'),

    Space    = device('devices.generic.FreeSpace',
                      description = 'The amount of free space for storing data',
                      path = None,
                      minfree = 5,
                     ),
)

startupcode = '''
if not Exp.proposal:
    SetMode('master')
    NewExperiment(0)
'''
