description = 'Email and SMS services'

group = 'lowlevel'

devices = dict(
    email    = device('devices.notifiers.Mailer',
                      description = 'Reports via email',
                      sender = 'rgeorgii@frm2.tum.de',
                      copies = [('rgeorgii@frm2.tum.de', 'all'),],
                      subject = 'MIRA',
                      lowlevel = True,
                     ),
    smser    = device('devices.notifiers.SMSer',
                      description = 'Reports via SMS',
                      server = 'triton.admin.frm2',
                      receivers = ['01719251564', '01782979497'],
                      lowlevel = True,
                     ),
)
