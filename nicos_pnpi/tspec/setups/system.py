description = 'system setup'

group = 'lowlevel'

sysconfig = dict(
    cache = 'localhost',
    instrument = 'Instrument',
    experiment = 'Exp',
    datasinks = ['conssink', 'filesink', 'daemonsink', 'livesink', 'sraw'],
    notifiers = ['email'],
)

modules = ['nicos.commands.standard']

includes = ['notifiers']

devices = dict(
    Instrument = device('nicos.devices.instrument.Instrument',
                        description = 'instrument object',
                        instrument = 'T-SPEC',
                        responsible = 'A. Sizov <sizov_aa@nrcki.pnpi.ru>',
                        facility = 'PNPI',
                        website = 'http://www.pnpi.spb.ru/'\
                                  'en/facilities/reactor-pik',
                        ),

    Sample = device('nicos.devices.sample.Sample',
                    description = 'The current used sample',
                    ),

    Exp = device('nicos.devices.experiment.Experiment',
                 description = 'experiment object',
                 dataroot = 'data',
                 sendmail = True,
                 serviceexp = 'service',
                 sample = 'Sample',
                 ),

    filesink = device('nicos.devices.datasinks.AsciiScanfileSink'),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    daemonsink = device('nicos.devices.datasinks.DaemonSink'),
    livesink = device('nicos.devices.datasinks.LiveViewSink'),
    sraw = device('nicos.devices.datasinks.SingleTextImageSink'),

)
