description = 'system setup only'

sysconfig = dict(
    cache = 'resi1',
    instrument = 'resiInstrument',
    experiment = 'Exp',
    notifiers = ['email'],
    datasinks = ['conssink', 'filesink', 'dmnsink'],
)

devices = dict(
    email    = device('devices.notifiers.Mailer',
                      sender = 'resi@resi2',
                      copies = ['bjoern.pedersen@frm2.tum.de'],
                      subject = 'RESI'),

    #smser    = device('devices.notifiers.SMSer',
    #                  server='triton.admin.frm2'),

    Exp      = device('resi.experiment.ResiExperiment',
                      sample = 'Sample',
                      dataroot = '/tmp/data/testdata',
                      _propdb = 'useroffice@tacodb.taco.frm2:useroffice'),

    resiInstrument =device('devices.instrument.Instrument',
                       instrument= 'RESI',
                        responsible ='BP'   ),

    filesink = device('devices.datasinks.AsciiDatafileSink'),

    conssink = device('devices.datasinks.ConsoleSink'),

    dmnsink  = device('devices.datasinks.DaemonSink'),

   # gracesink= device('devices.datasinks.GraceSink'),
)
