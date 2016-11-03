description = 'POLI standard setup'

group = 'basic'

includes = ['mono', 'slits', 'detector', 'table_tg']

devices = dict(
    POLI     = device('devices.sxtal.instrument.LiftingSXTal',
                      description = 'The POLI instrument',
                      responsible = 'V. Hutanu <vladimir.hutanu@frm2.tum.de>',
                      instrument = 'POLI',
                      doi = 'http://dx.doi.org/10.17815/jlsrf-1-22',
                      mono = 'wavelength',
                      gamma = 'gamma',
                      omega = 'sth',
                      nu = 'liftingctr',
                     ),

    Sample   = device('devices.sxtal.sample.SXTalSample',
                      description = 'The current used sample',
                     ),
)
