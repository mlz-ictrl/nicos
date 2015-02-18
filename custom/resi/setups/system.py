description = 'system setup only'
group = 'basic'

sysconfig = dict(
    cache = 'resi1',
    instrument = 'resiInstrument',
    experiment = 'Exp',
    notifiers = ['email'],
    datasinks = ['conssink', 'filesink', 'dmnsink'],
)

modules = ['nicos.commands.standard']

devices = dict(
    email = device('devices.notifiers.Mailer',
                      sender = 'bjoern.pedersen@frm2.tum.de',
                      copies = [('bjoern.pedersen@frm2.tum.de', 'all')],
                      subject = 'RESI'),

    #smser    = device('devices.notifiers.SMSer',
    #                  server='triton.admin.frm2'),

    Exp = device('resi.experiment.ResiExperiment',
                      sample = 'Sample',
                      dataroot = '/tmp/data/testdata',
                      localcontact = 'bjoern.pedersen@frm2.tum.de',
                      ),

    resiInstrument = device('devices.instrument.Instrument',
                       instrument = 'RESI',
                        responsible = 'BP <bjoern.pedersen@frm2.tum.de>'),

    Sample = device('devices.sample.Sample'),

    filesink = device('devices.datasinks.AsciiDatafileSink'),

    conssink = device('devices.datasinks.ConsoleSink'),

    dmnsink = device('devices.datasinks.DaemonSink'),
)
