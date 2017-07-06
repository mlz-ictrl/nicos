description = 'Email and SMS services'

group = 'lowlevel'

devices = dict(
    email    = device('devices.notifiers.Mailer',
                      description = 'Reports via email',
                      sender = 'puma@frm2.tum.de',
                      mailserver = 'smtp.frm2.tum.de',
                      copies = [('jitae.park@frm2.tum.de', 'all'),
                                ('Avishek.Maity@frm2.tum.de', 'all'),
                               ],
                      subject = 'PUMA',
                      lowlevel = True,
                     ),
    smser    = device('devices.notifiers.SMSer',
                      description = 'Reports via SMS',
                      server = 'triton.admin.frm2',
                      receivers = ['017680508564', '017655576167'],
                      lowlevel = True,
                     ),
)
