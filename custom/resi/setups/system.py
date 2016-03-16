description = 'system setup only'
group = 'basic'

sysconfig = dict(
    cache = 'resi1',
    instrument = 'resiInstrument',
    experiment = 'Exp',
    notifiers = ['email'],
    datasinks = ['conssink', 'filesink', 'dmnsink'],
)

modules = ['commands.standard']

devices = dict(
    email = device('devices.notifiers.Mailer',
                   description = 'The notifier to send emails',
                      sender = 'bjoern.pedersen@frm2.tum.de',
                      copies = [('bjoern.pedersen@frm2.tum.de', 'all')],
                      subject = 'RESI'),

    #smser    = device('devices.notifiers.SMSer',
    #                  server='triton.admin.frm2'),

    Exp = device('resi.experiment.ResiExperiment',
                 description = 'The currently running experiment',
                      sample = 'Sample',
                      dataroot = '/tmp/data/testdata',
                      ),

    resiInstrument = device('devices.instrument.Instrument',
                            description = 'Thermal neutron single crystal '
                                          'diffractometer',
                            instrument = 'RESI',
                            doi = 'http://dx.doi.org/10.17815/jlsrf-1-23',
                            responsible = 'B. Pedersen <bjoern.pedersen@frm2.tum.de>'),

    Sample = device('devices.sample.Sample',
                    description = 'The sample',
                   ),

    filesink = device('devices.datasinks.AsciiScanfileSink',
                      lowlevel = True,
                     ),

    conssink = device('devices.datasinks.ConsoleScanSink',
                      lowlevel = True,
                     ),

    dmnsink = device('devices.datasinks.DaemonSink',
                     lowlevel = True,
                    ),
)
