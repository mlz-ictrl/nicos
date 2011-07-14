name = 'system setup only'

sysconfig = dict(
    cache = 'resi2',
    instrument = 'resiInstrument',
    experiment = 'Exp',
    notifiers = ['email'],
    datasinks = ['conssink', 'filesink', 'dmnsink'],
)

devices = dict(
    email    = device('nicos.notify.Mailer',
                      sender = 'resi@resi2',
                      copies = ['bjoern.pedersen@frm2.tum.de'],
                      subject = 'RESI'),

    #smser    = device('nicos.notify.SMSer',
    #                  server='triton.admin.frm2'),

    Exp      = device('nicos.resi.experiment.ResiExperiment',
                      sample = 'Sample',
                      datapath = ['/tmp/data/testdata'],
                      _propdb = 'useroffice@tacodb.taco.frm2:useroffice'),

    resiInstrument =device('nicos.instrument.Instrument',
                       instrument= 'RESI',
                        responsible ='BP'   ),

    filesink = device('nicos.data.AsciiDatafileSink'),

    conssink = device('nicos.data.ConsoleSink'),

    dmnsink  = device('nicos.data.DaemonSink'),

   # gracesink= device('nicos.data.GraceSink'),
)
