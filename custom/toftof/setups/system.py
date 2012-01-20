description = 'NICOS system setup'

sysconfig = dict(
    cache = 'cpci1.toftof.frm2',
    instrument = 'TOFTOF',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink'],
    notifiers = [],
)

devices = dict(
    TOFTOF   = device('nicos.instrument.Instrument',
                      instrument = 'TOFTOF'),

    Sample   = device('nicos.experiment.Sample'),

    Exp      = device('nicos.experiment.Experiment',
                      datapath = ['/users/testdata'],
                      sample = 'Sample',
                      elog = False),

    filesink = device('nicos.data.AsciiDatafileSink',
                      prefix = 'data'),

    conssink = device('nicos.data.ConsoleSink'),

    daemonsink = device('nicos.data.DaemonSink'),

    Space    = device('nicos.generic.FreeSpace',
                      path = '/users',
                      minfree = 5),
)
